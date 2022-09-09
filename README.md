# Speech_To_Text_To_Speech

A Python program that utilizes the Microsoft Azure Speech to Text and Text to Speech APIs. This was originally created to help a friend of mine who struggles with ALS. The person in question is only able to speak at a very low volume - this was designed to basically replace the voice of the user to something louder and more understandable.

The program loops, first utilizing the Speech-to-Text API to listen to the user's microphone until something is heard. Once something is picked up by the microphone, the data is sent to the API, which then returns the transcribed speech. After this, the transcribed speech is passed straight into the Azure Text-to-Speech API. Following this, the API will play the newly AI-generated speech through the speakers or audio device of the users choice. The person this was designed for used a virtual microphone to output the audio instead of merely playing the audio through the speakers.

There are a few things that I would like to add to this project to make it more user friendly and generally more pleasant to use:

A push-to-talk function or some way to limit the API usage would be a great thing to have since the APIs being used are not free, nor are they very cheap. This would be the first thing I would complete, especially since the program is essentially double-dipping APIs.
Allowing the user to customize the voice that the AI speech generator uses would be a great option to have - possibly prompt the user with a simple GUI that shows them the voices available and generally what they sound like.
Allowing the user to control various other aspects of the voice would be good, including pitch, tone, etc. Basically anything that would allow the user to show more emotion or intent would be a great addition.
