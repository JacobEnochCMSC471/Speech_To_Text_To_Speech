import azure.cognitiveservices.speech as speechsdk
import winsound
import pynput
import time
import os


class STT_TTS:
    # ------------------------------Change API Key or Region Here------------------------------ #
    api_key = ""
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

    ssml_doc = open('voice_options.xml', 'r')

    # Attempts to transcribe speech into text using Azure STT API
    def speech_to_text(self):
        print("Waiting for audio input...")
        speech_to_text = self.speech_recognizer.recognize_once_async().get()
        print("Audio input found!\n")

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
    # This ended up being un-used because it's very inflexible with how the TTS is spoken - no prosody, mood or pitch changes AFAIK
    def text_to_speech(self, stt_result):
        if stt_result == 'Error':
            print(stt_result)
            return

        elif stt_result.reason == speechsdk.ResultReason.RecognizedSpeech:  # Speech was successfully recognized
            speech_synthesis_result = self.speech_synthesizer.speak_text_async(stt_result.text).get()  # Retrieve the TTS result
            actual_text = stt_result.text

            if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:  # Print transcribed speech to console
                print("Transcribed Speech: {}".format(actual_text))
                return actual_text

            # The speech synthesis was cancelled for some reason - print the errors and return
            elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
                print("Speech synthesis canceled: {}".format(cancellation_details.reason))

                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")
                    return
        return


def get_voice_options():
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

    # A list of tones that the TTS-generated voice can take on
    tone_list = [
        'affectionate',
        'angry',
        'calm',
        'chat',
        'cheerful',
        'depressed',
        'disgruntled',
        'embarrassed',
        'empathetic',
        'envious',
        'excited',
        'fearful',
        'friendly',
        'gentle',
        'hopeful',
        'sad',
        'serious',
        'unfriendly'
    ]

    # Input of 0 means -50% pitch in Azure; Input of 0.5 means +50% pitch in Azure, -0.5 = -50% pitch in Azure
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

    # If the user-typed voice is not in the key list, continue looping until they enter correct value
    while chosen_voice not in key_list:
        print('Choice not found!')
        chosen_voice = input('Please type your voice choice exactly as you see it: ')

    # Extract the chosen voice Azure format
    actual_voice = voices_female_dict[chosen_voice]

    print('\n-----List of Tones-----')

    for tone in tone_list:
        print(tone)

    chosen_tone = input('Please type your chosen tone exactly as you see it: ')

    while chosen_tone not in tone_list:
        chosen_tone = input('Choice not found! Please type your chosen tone exactly as you see it: ')

    choice_dict = {
        'Pitch': pitch,
        'Speaking Speed': speaking_speed,
        'Voice': actual_voice,
        'Tone': chosen_tone
    }

    return choice_dict


# This file will directly write SSML (Speech Synthesis Markup Language) to a file in order to edit speed, tone and voice
def write_to_xml_file(user_choices, text):
    # Extract the individual user choices and store them in easily formatted variables
    voice = user_choices.get('Voice')
    talk_speed = int(user_choices.get('Speaking Speed') * 100)
    pitch = int(user_choices.get('Pitch') * 100)
    tone = user_choices.get('Tone')

    xml_file = open('voice_options.xml', 'w')

    # Write an XML file using the SSML documentation found at the link below:
    # https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp

    xml_file.write(
        '<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">\n')
    xml_file.write('    <voice name="{}">\n'.format(voice))
    xml_file.write('        <mstts:express-as role="YoungAdultFemale" style="{}">\n'.format(tone))
    xml_file.write('            <prosody rate="{}%" pitch="{}%">\n'.format(talk_speed, pitch))
    xml_file.write('                {}\n'.format(text))
    xml_file.write('            </prosody>\n')
    xml_file.write('        </mstts:express-as>\n')
    xml_file.write('    </voice>\n')
    xml_file.write('</speak>')

    xml_file.close()

    return


# This function reads an XML file contents and returns it as a string (used in TTS portion)
def read_xml_file(file):
    file = open(file)
    xml_string = ''

    for line in file:
        xml_string += line

    file.close()

    return xml_string


# This function takes an event returned by pynput.keyboard.Events() and parses only the selected key out of the output of this function
def parse_events(event):
    event_string = str(event)

    if "Press" in event_string:
        split_word = event_string.split('Press(key=')
        actual_key = split_word[1].strip("'")
        actual_key = actual_key.strip("')")

    else:
        split_word = event_string.split('Release(key=')
        actual_key = split_word[1].strip("'")
        actual_key = actual_key.strip("')")

    return actual_key


def main():
    # Ask the user to define the pitch, talking speed, voice and tone of the text-to-speech output
    user_choices = get_voice_options()

    print('Please enter the key you would like to use as a TTS hotkey: ')
    time.sleep(0.5)

    with pynput.keyboard.Events() as hotkey_event:
        initial_event = hotkey_event.get(10)

        if initial_event is None:
            print("Please enter a valid key to use as a valid TTS hotkey. Program exiting...")
            exit(0)

        else:
            chosen_hotkey = parse_events(initial_event)

    sst_tts_obj = STT_TTS()

    print('\nRecording of speech for TTS purposes will begin when you press the {}. This will loop until closed.\n'.format(chosen_hotkey))

    # This will loop forever or until the program is stopped.
    while True:
        with pynput.keyboard.Events() as events:
            # Block at most one second
            event = events.get(.1)

            if event is None:
                continue

            else:
                actual_key = parse_events(event)

            if actual_key != chosen_hotkey:
                continue

            else:
                speech_to_text_result = sst_tts_obj.speech_to_text()

                # Errors occurring during the STT process will be printed earlier than this, hence the continue
                if speech_to_text_result == 'Error':
                    continue

                # Extract the text from the STT API
                transcribed_text = speech_to_text_result.text

                # Write the extracted text to an XML file using SSML (Synthesized Speech Markup Language)
                write_to_xml_file(user_choices, transcribed_text)

                # Convert the XML file to a standard string
                xml_file_text = read_xml_file('voice_options.xml')

                # Use the SSML string in the TTS API
                sst_tts_obj.speech_synthesizer.speak_ssml(xml_file_text)


main()
