# MeetingTextMemo

Welcome to Tony's project information page!


## Why: Convo

* Context: Many meetings and not enough hands. Automatically condense the information into a recorded/live audio into a meeting summary.
* Need: Keep records. Reduce labor. Help focus. Give highlights to unavailable audiences.
* Vision: Process recorded/live audio to generate variable length textual summaries of meeting highlights.
* Outcome: Short product: at the end of every audio presentation, a generated text summary. In the future, this could be integrated into Zoom/Skype or whatever meeting/voice software.


## Product and milestones

* Input: recorded wav files; live voices
* Output: user tunable variable length texts by the end of the *live* meeting
* Back-end: python

* MVP: Record live conversation, return a few keywords.
* Full product: Record live conversation, return comprehensible sentences.
* Further: Use audio characteristics to catch questions, change of volume and tone to help NLP recognition.


## List of Todo's For Jun 12, 2018

* Add in a google API option for speech recognition. -- Added; but needs internet.
* Add Ted talks -- NCE is too far away from this audience. (NPR added.)
* Serious NLP?/ Performance score? ROUGE.
* Data exploration? CNN data.
* Train on some text recongnition and then test on recognised speech? Yes.
* Demo suggestion? Flask? 
* Keyword summary/Headline summary/Informative summary/Indicative summary

* Format the CNN text input to x and Y
* Text to text summarization templates running and ready


## Open Questions

* Deal with multi-speaker
* Deal with many topics, how granular are the summaries
* Identify important parts of the conversation / meeting
* Combination with fixed agenda
