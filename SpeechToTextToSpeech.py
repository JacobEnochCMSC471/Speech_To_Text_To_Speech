import azure.cognitiveservices.speech as speechsdk
import winsound

# ------------------------------Change API Key or Region Here------------------------------ #
api_key = ""
region = "eastus"  # Region in which the service was registered - can be located where the API keys are found on Azure website
language = "en-US"  # Language that the speech recognition software will be expecting when transcribing
# ----------------------------------------------------------------------------------------- #

speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
speech_config.speech_recognition_language = language  # Set the language that the speech recognition API will be transcribing from
speech_config.speech_synthesis_voice_name = 'en-US-SaraNeural'  # Set the voice of the TTS program
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

while True:
    print("Waiting for audio input...\n")
    speech_to_text = speech_recognizer.recognize_once_async().get()
    actual_text = speech_to_text.text

    # ---------------------------Transcribing worked--------------------------- #

    if speech_to_text.reason == speechsdk.ResultReason.RecognizedSpeech:  # Speech was successfully recognized
        # Use newly transcribed text in a TTS program now that the speech was recognized and transcribed successfully
        speech_synthesis_result = speech_synthesizer.speak_text_async(actual_text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:  #
            print("Transcribed Speech: ".format(actual_text))

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))

            if cancellation_details.reason == speechsdk.CancellationReason.Error:

                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")

    # ---------------------------Errors--------------------------- #

    elif speech_to_text.reason == speechsdk.ResultReason.NoMatch:  # No speech was recognized, try again
        print("No speech could be recognized: {}".format(speech_to_text.no_match_details))
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
        continue

    elif speech_to_text.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_to_text.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

        break

# Assuming that a fatal error occured, play an alert sound and print a message that the
winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
print("An error occurred, please see the provided error message for diagnosing.\n")
