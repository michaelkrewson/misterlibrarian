// On-device speech-to-text for a single audio file. Prints the transcript on
// stdout, diagnostics on stderr, and sends nothing over the network.
//
// Driven by tools/travel_transcribe.py — see that file for the why. Two things
// in here are load-bearing and non-obvious:
//
//   1. This uses SpeechAnalyzer/SpeechTranscriber (macOS 26+), NOT the older
//      SFSpeechRecognizer. The old API goes through a TCC privacy check that
//      *hard-crashes* a command-line binary (SIGABRT, no error, no output) even
//      when an Info.plist with NSSpeechRecognitionUsageDescription is linked
//      into the executable. SpeechAnalyzer does file transcription without that
//      permission prompt at all, which is what makes this scriptable.
//
//   2. The results stream has to be drained CONCURRENTLY with the analysis.
//      Calling analyzeSequence first and reading transcriber.results after it
//      returns will hang: the analyzer is waiting for someone to consume the
//      results it is producing.
//
// The speech model is a one-time download the first time a locale is used.
// AssetInventory handles it; that is the only step that needs a network
// connection, and it is about the model, never about the audio.

import Foundation
import Speech
import AVFoundation

func note(_ s: String) {
    FileHandle.standardError.write((s + "\n").data(using: .utf8)!)
}

@main
struct TravelTranscribe {
    static func main() async {
        var args = Array(CommandLine.arguments.dropFirst())
        var localeID = "en-US"

        if let i = args.firstIndex(of: "--locale"), i + 1 < args.count {
            localeID = args[i + 1]
            args.removeSubrange(i...(i + 1))
        }
        guard let path = args.first else {
            note("usage: travel_transcribe <audio-file> [--locale en-US]")
            exit(2)
        }

        let url = URL(fileURLWithPath: path)
        guard FileManager.default.fileExists(atPath: url.path) else {
            note("no such file: \(url.path)")
            exit(2)
        }

        do {
            let transcriber = SpeechTranscriber(
                locale: Locale(identifier: localeID),
                transcriptionOptions: [],
                reportingOptions: [],
                attributeOptions: []
            )

            let installed = await SpeechTranscriber.installedLocales
            note("locale \(localeID); \(installed.count) locale(s) installed")

            // No-op once the model for this locale is on disk.
            if let request = try await AssetInventory.assetInstallationRequest(
                supporting: [transcriber]
            ) {
                note("downloading the \(localeID) speech model (one time)…")
                try await request.downloadAndInstall()
                note("model installed")
            }

            let analyzer = SpeechAnalyzer(modules: [transcriber])
            let audio = try AVAudioFile(forReading: url)

            // Must start BEFORE analyzeSequence — see note 2 at the top.
            let collector = Task { () -> String in
                var out = AttributedString()
                for try await result in transcriber.results {
                    out += result.text
                }
                return String(out.characters)
            }

            _ = try await analyzer.analyzeSequence(from: audio)
            try await analyzer.finalizeAndFinishThroughEndOfInput()

            let text = try await collector.value
                .trimmingCharacters(in: .whitespacesAndNewlines)
            if text.isEmpty {
                note("no speech recognised — is there audible speech in this file?")
                exit(1)
            }
            print(text)
            exit(0)
        } catch {
            note("ERROR: \(error)")
            exit(7)
        }
    }
}
