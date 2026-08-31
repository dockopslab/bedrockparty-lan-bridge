package main

import (
	"context"
	cryptorand "crypto/rand"
	"encoding/binary"
	"encoding/hex"
	"errors"
	"fmt"
	"log/slog"
	"net"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/df-mc/go-nethernet"
	"github.com/df-mc/go-nethernet/discovery"
	"github.com/pion/ice/v4"
	"github.com/pion/webrtc/v4"
	"github.com/sandertv/gophertunnel/minecraft"
	"github.com/sandertv/gophertunnel/minecraft/protocol/login"
	"github.com/sandertv/gophertunnel/minecraft/protocol/packet"
)

type config struct {
	listenAddress string
	backend       string
	networkID     uint64
	serverName    string
	levelName     string
	gameType      int32
	players       int32
	maxPlayers    int32
	publicIP      string
	icePort       int
	logLevel      slog.Level
}

// fixedDiscoveryNetwork prevents generic gophertunnel RakNet state from
// periodically replacing NetherNet LAN ServerData v6, including its nonce.
type fixedDiscoveryNetwork struct {
	minecraft.Network
	discoveryListener *discovery.Listener
	serverData        *discovery.ServerData
}

func (n fixedDiscoveryNetwork) Listen(address string) (minecraft.NetworkListener, error) {
	listener, err := n.Network.Listen(address)
	if err != nil {
		return nil, err
	}
	n.discoveryListener.ServerData(n.serverData)
	return fixedPongListener{NetworkListener: listener}, nil
}

type fixedPongListener struct {
	minecraft.NetworkListener
}

func (fixedPongListener) PongData([]byte) {}

func main() {
	cfg, err := loadConfig()
	if err != nil {
		slog.Error("invalid configuration", "error", err)
		os.Exit(1)
	}
	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: cfg.logLevel}))
	slog.SetDefault(logger)

	settingEngine := webrtc.SettingEngine{}
	iceConn, err := net.ListenUDP("udp4", &net.UDPAddr{IP: net.IPv4zero, Port: cfg.icePort})
	if err != nil {
		logger.Error("listen on ICE UDP port", "port", cfg.icePort, "error", err)
		os.Exit(1)
	}
	udpMux := ice.NewUDPMuxDefault(ice.UDPMuxParams{UDPConn: iceConn})
	defer udpMux.Close()
	settingEngine.SetICEUDPMux(udpMux)
	if cfg.publicIP != "" {
		settingEngine.SetNAT1To1IPs([]string{cfg.publicIP}, webrtc.ICECandidateTypeHost)
	}
	api := webrtc.NewAPI(webrtc.WithSettingEngine(settingEngine))

	discoveryListener, err := (discovery.ListenConfig{NetworkID: cfg.networkID, Log: logger}).Listen(cfg.listenAddress)
	if err != nil {
		logger.Error("listen for NetherNet LAN discovery", "error", err)
		os.Exit(1)
	}
	defer discoveryListener.Close()

	nonce, err := randomNonce()
	if err != nil {
		logger.Error("generate discovery nonce", "error", err)
		os.Exit(1)
	}
	serverData := &discovery.ServerData{
		ServerName:            cfg.serverName,
		LevelName:             cfg.levelName,
		GameType:              cfg.gameType,
		PlayerCount:           cfg.players,
		MaxPlayerCount:        cfg.maxPlayers,
		AcceptsOnlineAuth:     true,
		AcceptsSelfSignedAuth: true,
		Nonce:                 nonce,
		TransportLayer:        discovery.TransportLayerNetherNet,
		ConnectionType:        4,
	}

	netherNet := minecraft.NetherNet{
		Signaling: discoveryListener,
		ListenConfig: nethernet.ListenConfig{
			API:            api,
			AllowAnonymous: true,
			Log:            logger,
			NegotiationContext: func(parent context.Context) (context.Context, context.CancelFunc) {
				return context.WithTimeout(parent, 20*time.Second)
			},
			ConnContext: func(parent context.Context, _ *nethernet.Conn) (context.Context, context.CancelFunc) {
				return context.WithTimeout(parent, 20*time.Second)
			},
		},
		Log: logger,
	}
	network := fixedDiscoveryNetwork{
		Network:           netherNet,
		discoveryListener: discoveryListener,
		serverData:        serverData,
	}
	listener, err := (minecraft.ListenConfig{
		AuthenticationDisabled: true,
		MaximumPlayers:         int(cfg.maxPlayers),
		ErrorLog:               logger,
		StatusProvider:         minecraft.NewStatusProvider(cfg.levelName, cfg.serverName),
	}).ListenNetwork(network, discoveryListener.NetworkID())
	if err != nil {
		logger.Error("start Minecraft NetherNet listener", "error", err)
		os.Exit(1)
	}
	defer listener.Close()

	logger.Info("BedrockParty NetherNet bridge ready", "listen", cfg.listenAddress, "backend", cfg.backend,
		"networkID", cfg.networkID, "publicIP", cfg.publicIP,
		"icePort", fmt.Sprintf("%d/udp", cfg.icePort), "world", cfg.levelName)
	for {
		accepted, err := listener.Accept()
		if err != nil {
			if !errors.Is(err, net.ErrClosed) {
				logger.Error("accept NetherNet client", "error", err)
			}
			return
		}
		conn := accepted.(*minecraft.Conn)
		logger.Info("NetherNet client connected", "remote", conn.RemoteAddr())
		go bridge(conn, listener, cfg.backend, logger)
	}
}

func bridge(client *minecraft.Conn, listener *minecraft.Listener, backendAddress string, logger *slog.Logger) {
	identity := client.IdentityData()
	clientData := client.ClientData()
	if identity.DisplayName == "" && identity.XUID == "" {
		displayName, nameSource := offlineClientDisplayName(identity, clientData)
		identity.DisplayName = displayName
		logger.Info("assigned local name to offline client", "remote", client.RemoteAddr(),
			"displayName", identity.DisplayName, "source", nameSource)
	}
	backend, err := (minecraft.Dialer{
		ClientData:   clientData,
		IdentityData: identity,
		ErrorLog:     logger,
		PacketFunc: func(header packet.Header, payload []byte, source, destination net.Addr) {
			if header.PacketID != packet.IDDisconnect || len(payload) > 64 {
				return
			}
			attributes := []any{"hex", hex.EncodeToString(payload), "source", source, "destination", destination}
			if reason, ok := disconnectReason(payload); ok {
				attributes = append(attributes, "reason", reason)
				if reason == 46 {
					attributes = append(attributes, "reasonName", "NotAuthenticated")
				}
			}
			logger.Info("backend disconnect", attributes...)
		},
	}).DialContext(client.Context(), "raknet", backendAddress)
	if err != nil {
		logger.Error("connect to Bedrock backend", "remote", client.RemoteAddr(), "backend", backendAddress, "error", err)
		_ = listener.Disconnect(client, "Could not connect to BedrockParty")
		return
	}
	defer backend.Close()

	var start sync.WaitGroup
	start.Add(2)
	var startErr error
	var startMu sync.Mutex
	recordStartError := func(err error) {
		if err != nil {
			startMu.Lock()
			if startErr == nil {
				startErr = err
			}
			startMu.Unlock()
		}
		start.Done()
	}
	go func() { recordStartError(client.StartGame(backend.GameData())) }()
	go func() { recordStartError(backend.DoSpawn()) }()
	start.Wait()
	if startErr != nil {
		logger.Error("start proxied game", "remote", client.RemoteAddr(), "error", startErr)
		_ = listener.Disconnect(client, "Could not start BedrockParty")
		return
	}

	logger.Info("Bedrock session bridged", "remote", client.RemoteAddr(), "backend", backendAddress)
	done := make(chan struct{}, 2)
	go relayPackets(client, backend, done)
	go relayPackets(backend, client, done)
	<-done
	_ = listener.Disconnect(client, "Connection closed")
	logger.Info("Bedrock session closed", "remote", client.RemoteAddr())
}

func offlineClientDisplayName(identity login.IdentityData, clientData login.ClientData) (string, string) {
	candidate := strings.TrimSpace(clientData.ThirdPartyName)
	withCandidate := identity
	withCandidate.DisplayName = candidate
	if candidate != "" && withCandidate.Validate() == nil {
		return candidate, "thirdPartyName"
	}
	return offlineDisplayName(identity.Identity), "generated"
}

func disconnectReason(payload []byte) (int32, bool) {
	value, bytesRead := binary.Uvarint(payload)
	if bytesRead <= 0 || value > uint64(^uint32(0)) {
		return 0, false
	}
	encoded := uint32(value)
	return int32(encoded>>1) ^ -int32(encoded&1), true
}

func offlineDisplayName(identity string) string {
	suffix := strings.ReplaceAll(identity, "-", "")
	if len(suffix) > 8 {
		suffix = suffix[:8]
	}
	if suffix == "" {
		suffix = "Local"
	}
	return "Switch" + suffix
}

func relayPackets(source, destination *minecraft.Conn, done chan<- struct{}) {
	defer func() { done <- struct{}{} }()
	for {
		// ReadBytes/Write preserves the complete Bedrock header, including the
		// SenderSubClient and TargetSubClient IDs used by local console multiplayer.
		data, err := source.ReadBytes()
		if err != nil {
			return
		}
		if _, err := destination.Write(data); err != nil {
			return
		}
	}
}

func randomNonce() (string, error) {
	b := make([]byte, 8)
	if _, err := cryptorand.Read(b); err != nil {
		return "", err
	}
	return hex.EncodeToString(b), nil
}

func loadConfig() (config, error) {
	port := envInt("NETHERNET_PORT", 7551)
	serverID, err := strconv.ParseUint(env("NETHERNET_SERVER_ID", "1234567890123456789"), 10, 64)
	if err != nil {
		return config{}, fmt.Errorf("NETHERNET_SERVER_ID: %w", err)
	}
	icePort := envInt("NETHERNET_ICE_PORT", 50000)
	var logLevel slog.Level
	if err := logLevel.UnmarshalText([]byte(env("LOG_LEVEL", "INFO"))); err != nil {
		return config{}, fmt.Errorf("LOG_LEVEL: %w", err)
	}
	if port < 1 || port > 65535 || icePort < 1 || icePort > 65535 {
		return config{}, errors.New("invalid UDP port")
	}
	return config{
		listenAddress: net.JoinHostPort(env("NETHERNET_LISTEN_IP", "0.0.0.0"), strconv.Itoa(port)),
		backend:       net.JoinHostPort(env("BACKEND_IP", "127.0.0.1"), env("BACKEND_PORT", "19132")),
		networkID:     serverID,
		serverName:    env("NETHERNET_SERVER_NAME", "BedrockParty"),
		levelName:     env("NETHERNET_LEVEL_NAME", "BedrockParty"),
		gameType:      int32(envInt("NETHERNET_GAME_TYPE", 0)),
		players:       int32(envInt("PLAYERS", 0)),
		maxPlayers:    int32(envInt("MAX_PLAYERS", 10)),
		publicIP:      os.Getenv("NETHERNET_PUBLIC_IP"),
		icePort:       icePort,
		logLevel:      logLevel,
	}, nil
}

func env(name, fallback string) string {
	if value := os.Getenv(name); value != "" {
		return value
	}
	return fallback
}

func envInt(name string, fallback int) int {
	value := os.Getenv(name)
	if value == "" {
		return fallback
	}
	parsed, err := strconv.Atoi(value)
	if err != nil {
		return fallback
	}
	return parsed
}
