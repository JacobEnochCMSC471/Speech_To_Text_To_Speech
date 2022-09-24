import azure.cognitiveservices.speech as speechsdk
import winsound
from pynput.keyboard import Key, Listener


class STT_TTS:
    # ------------------------------Change API Key or Region Here------------------------------ #
    api_key = "27c0ca7564674676945b2b26f497c457"
    region = "eastus"  # Region in which the service was registered - can be located where the API keys are found on Azure website
    language = "en-US"  # Language that the speech recognition software will be expecting when transcribing
    # ----------------------------------------------------------------------------------------- #

    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    speech_config.speech_recognition_language = language  # Set the language that the speech recognition API will be transcribing from
    speech_config.speech_synthesis_voice_name = 'en-US-SaraNeural'  # Set the voice of the TTS program
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    # The speech recognizer uses the Azure STT (speech-to-text) API to listen to audio input - if it exists it is sent to the API for processing
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # The speech synthesizer uses the Azure TTS (text-to-speech) API to convert text input into an AI-generated audio output
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Attempts to transcribe speech into text using Azure STT API
    def speech_to_text(self):
        print("Waiting for audio input...\n")
        speech_to_text = self.speech_recognizer.recognize_once_async().get()

        if speech_to_text.reason == speechsdk.ResultReason.NoMatch:  # No speech was recognized, return error
            print("No speech could be recognized: {}".format(speech_to_text.no_match_details))
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
            return "Error"

        elif speech_to_text.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_to_text.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
            return "Error"

        return speech_to_text

    # Uses the result from speech_to_text() in the TTS Azure API
    def text_to_speech(self, stt_result):
        if stt_result.reason == speechsdk.ResultReason.RecognizedSpeech:  # Speech was successfully recognized
            speech_synthesis_result = self.speech_synthesizer.speak_text_async(stt_result.text).get()  # Retrieve the TTS result

            if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:  # Print transcribed speech to console
                print("Transcribed Speech: ".format(speech_synthesis_result.text))
                return speech_synthesis_result.text

            elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
                print("Speech synthesis canceled: {}".format(cancellation_details.reason))

                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")
                    return "Error"


def set_voice():
    print(
        'Previews of voices can be found at this website: https://azure.microsoft.com/en-us/products/cognitive-services/text-to-speech/#features')

    # Dictionary of female voices that Azure offers
    voices_female_dict = {
        'Jenny': 'en-US-JennyNeural',
        'Amber': 'en-US-AmberNeural',
        'Ana': 'en-US-AnaNeural',
        'Aria': 'en-US-AriaNeural',
        'Ashley': 'en-US-AshleyNeural',
        'Cora': 'en-US-CoraNeural',
        'Elizabeth': 'en-US-ElizabethNeural',
        'Michelle': 'en-US-MichelleNeural',
        'Monica': 'en-US-MonicaNeural',
        'Sara': 'en-US-SaraNeural',
        'Jane': 'en-US-JaneNeural'
    }

    # Input of 0 means -50% pitch in Azure; Input of 1 means +50% pitch in Azure
    pitch = speaking_speed = -2

    while pitch > 0.5 or pitch < -0.5:

        pitch = float(input('Enter a pitch value between -0.5 and 0.5 (0 = Default): '))

        if pitch > 0.5 or pitch < -0.5:
            print('Incorrect input! Please try again.')

    # Input of -1 = -100% talking speed; Input of 2.0 = 200% talking speed
    while speaking_speed < -1.0 or speaking_speed > 2.0:
        speaking_speed = float(input('Enter a speaking speed between -1.0 and 2.0 (0.0 = Default): '))

        if speaking_speed < -1.0 or speaking_speed > 2.0:
            print('Incorrect input! Please try again..')

    # Print the list of available voices
    print("\n-----List of voices-----")

    key_list = []

    for key in voices_female_dict:
        key_list.append(key)
        print(key)

    # Have the user type in their voice of choice
    chosen_voice = input('\nPlease type your voice choice exactly as you see it: ')

    while chosen_voice not in key_list:
        print('Choice not found!')
        chosen_voice = input('Please type your voice choice exactly as you see it: ')

    # Extract the chosen voice Azure format
    actual_voice = voices_female_dict[chosen_voice]

    choice_dict = {
        'Pitch': pitch,
        'Speaking Speed': speaking_speed,
        'Voice': actual_voice
    }

    return choice_dict


# Monitors keystrokes in the background - does not save anything and rewrites the file each time the function is ran
def on_press(key):
    file = open("temp_fix.txt", 'w')
    key_string = str(key)
    stripped_key_string = key_string.replace("'", "")
    print(stripped_key_string)
    file.write(stripped_key_string)


set_voice()
