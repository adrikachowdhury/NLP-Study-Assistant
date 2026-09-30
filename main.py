from chatbot import ask_gemini, conversation, clear_conversation
from prompts import practice_prompt, feedback_prompt, concept_prompt

print("""
🧠 Welcome to your NLP Study Assistant!
Learn NLP concepts, practise your knowledge, and get feedback as you go!
""")

# continuing forever until we explicitly stop the loop by saying quit
while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() == "/help":
        # """- multi-line string in Python (triple-quoted string)
        print(""" Available commands:
            /help      -  Show available commands
            /learn     -  Start learning NLP concepts
            /practice  -  Start a practice question
            /summary   -  Show conversation summary (message count, tokens)
            /clear     -  Clear conversation history
            /trim      -  Trim conversation history
            /history   -  Show conversation history
            /quit      -  Exit the conversation
        """)
        continue # continues with the loop

    if user_input.lower() == "/learn":
        topic = input("Enter an NLP concept: ")

        if topic.strip().lower() == "/quit":
            print("Alright! Reach out to me whenever you need to learn any concept.")
            continue

        if not topic.strip():
            print("Please enter a topic.")
            continue

        prompt = concept_prompt(topic)
        ask_gemini(prompt)
        continue

    if user_input.lower() == "/summary":
        message_count, approximate_tokens = conversation.get_summary()
        
        print(f"\n--- Conversation Summary ---")
        print(f"Messages: {message_count}")
        print(f"Approximate tokens: {approximate_tokens}")

        continue

    if user_input.lower() == "/clear":
        clear_conversation()
        print("Conversation history cleared.")
        continue

    if user_input.lower() == "/history":
        print(conversation.get_history())
        continue

    if user_input.lower() == "/practice":
        topic = input("Enter an NLP topic: ")

        if topic.strip().lower() == "/quit":
            print("Alright! Reach out to me whenever you need to practice any concept.")
            continue

        # input validation
        # is there anything left after removing leading/trailing spaces from the string? if not, then it's empty
        if not topic.strip():
            print("Please enter a topic.")
            continue

        prompt = practice_prompt(topic)
        practice_question = ask_gemini(prompt) # storing ans in a variable

        if practice_question != "":
            student_answer = input("\nYour answer: ").strip()

            if not student_answer:
                print("Please provide an answer.")
                continue

            feedback = feedback_prompt(topic, student_answer)
            ask_gemini(feedback)

        continue

    if user_input.lower() == "/trim":
        try:
            max_messages = int(input("Enter the number of messages you want to keep: "))
            
            if max_messages < 1:
                print("Please enter a positive integer number.")
                continue

            conversation.trim_history(max_messages)

            print(f"Conversation history trimmed to the last {max_messages} messages.")

        # input() returns a string
        # int() raises ValueError if it cannot convert it to an integer
        except ValueError:
            print("Invalid input. Please enter a valid positive integer.")
        continue

    if user_input.lower() == "/quit":
        print("Goodbye!")
        break

    ask_gemini(user_input)