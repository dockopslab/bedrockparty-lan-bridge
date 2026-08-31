package main

import (
	"testing"

	"github.com/sandertv/gophertunnel/minecraft/protocol/login"
)

func TestOfflineDisplayName(t *testing.T) {
	tests := []struct {
		name     string
		identity string
		want     string
	}{
		{name: "uuid", identity: "4b28867e-1234-5678-90ab-cdef01234567", want: "Switch4b28867e"},
		{name: "empty", identity: "", want: "SwitchLocal"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := offlineDisplayName(test.identity); got != test.want {
				t.Fatalf("offlineDisplayName(%q) = %q, want %q", test.identity, got, test.want)
			}
		})
	}
}

func TestOfflineIdentityValidation(t *testing.T) {
	offline := login.IdentityData{Identity: "4b28867e-1234-5678-90ab-cdef01234567"}
	if err := offline.Validate(); err != nil {
		t.Fatalf("offline Switch identity with empty DisplayName was rejected: %v", err)
	}

	online := login.IdentityData{XUID: "123", Identity: "4b28867e-1234-5678-90ab-cdef01234567"}
	if err := online.Validate(); err == nil {
		t.Fatal("online identity with empty DisplayName was accepted")
	}
}

func TestOfflineClientDisplayName(t *testing.T) {
	identity := login.IdentityData{Identity: "4b28867e-1234-5678-90ab-cdef01234567"}
	tests := []struct {
		name       string
		clientName string
		want       string
		wantSource string
	}{
		{name: "Nintendo profile", clientName: "Player One", want: "Player One", wantSource: "thirdPartyName"},
		{name: "trim whitespace", clientName: "  Player Two  ", want: "Player Two", wantSource: "thirdPartyName"},
		{name: "empty fallback", clientName: "", want: "Switch4b28867e", wantSource: "generated"},
		{name: "invalid fallback", clientName: "123Player", want: "Switch4b28867e", wantSource: "generated"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got, source := offlineClientDisplayName(identity, login.ClientData{ThirdPartyName: test.clientName})
			if got != test.want || source != test.wantSource {
				t.Fatalf("offlineClientDisplayName() = (%q, %q), want (%q, %q)", got, source, test.want, test.wantSource)
			}
		})
	}
}

func TestDisconnectReason(t *testing.T) {
	reason, ok := disconnectReason([]byte{0x5c, 0x00, 0x00, 0x00})
	if !ok || reason != 46 {
		t.Fatalf("disconnectReason() = (%d, %t), want (46, true)", reason, ok)
	}
}
