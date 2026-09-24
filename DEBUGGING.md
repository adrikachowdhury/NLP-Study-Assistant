# Debugging Notes

## 1. Gemini API Connection

### Goal

Test whether the Python application could successfully connect to the Gemini API and receive a response.

### Issue 1: 404 Model Not Found

#### Initial code

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain NLP in one simple sentence."
)
```

#### Error

```text
404 NOT_FOUND
This model is no longer available to new users.
```

#### What happened

The application was successfully reaching Google's Gemini API, but the requested model was not available for the account. Therefore, the problem was not the API key or the Python environment.

The issue was that the requested model was unavailable.

#### Fix

I switched to the newer Gemini Interactions API and a currently available model.

### Issue 2: Wrong API Parameter

After switching to the Interactions API, the next error was caused by using the wrong parameter name.

#### Initial code

```python
interaction = client.interactions.create(
    model="gemini-3.6-flash",
    contents="Explain NLP in one simple sentence."
)
```

#### Error

```text
TypeError: create() got unexpected keyword argument(s): contents
```

#### What happened

The `interactions.create()` method expects the user's request under the `input` parameter, not `contents`.

#### Fix

I replaced the name `contents` with `input`.

### What I Learned

* A `404` model error does not necessarily mean that the API connection is broken. The API can be reachable while the requested model is unavailable.
* API methods have specific parameter names. `contents` and `input` are not interchangeable.
* Reading the traceback helps identify the immediate source of an error.
* When an API call fails, first determine whether the problem is related to the environment, authentication, model availability, API method, or parameters before changing the whole implementation.
* API documentation and available models can change, so older tutorials may no longer work even when the general approach remains valid.

## 2. Off-Topic Question Behaviour

### Issue

I tested the chatbot with the question:

```text
Where is Asia?
```

The chatbot answered the factual question, but then unnecessarily reframed the response as an NLP lesson and generated an NLP-related practice question.

### What happened

The system prompt strongly encouraged the assistant to explain NLP concepts and provide NLP-focused learning support. Because of this, the assistant sometimes tried to connect questions outside the intended domain to NLP instead of recognising that they were unrelated.

### Fix

I updated the `SYSTEM_PROMPT` in `prompts.py` to explicitly define how the assistant should handle questions unrelated to NLP.

The updated instruction tells the assistant to:

* Answer simple unrelated questions briefly when appropriate.
* Avoid forcing an NLP connection.
* Politely redirect the user toward NLP-related topics when appropriate.

### Lesson

A system prompt should define not only what an AI assistant should do, but also how it should behave when a user's request falls outside its intended scope.

This was a prompt-level issue rather than a Python or API error.

## 3. Streaming Error Handling

### Issue

While testing streaming responses, I initially assumed that if the `for event in stream` loop finished, the request had succeeded.

However, this was not necessarily true.

Gemini can send an `error` event during a streaming interaction instead of completing the interaction successfully.

A successful interaction follows a sequence such as:

```text
interaction.created → step.delta → step.delta → interaction.completed
```

Receiving some streamed text does not necessarily mean that the interaction completed successfully.

### What happened

During one test, the model was under high demand and the streaming interaction produced an error before completion.

The initial implementation did not explicitly handle the streaming `error` event. As a result, an incomplete response could be treated as if the request had finished normally.

This also meant that the incomplete response should not be added to the conversation history.

### Fix

I added explicit handling for the `error` event:

```python
elif event.event_type == "error":
    raise RuntimeError(str(event.error))
```

This causes the streaming error to:

1. Raise an exception.
2. Exit the current `try` block.
3. Be caught by the `except` block.
4. Enter the existing retry logic.
5. Retry the Gemini request when the error is transient.

The completed interaction ID is only saved when an `interaction.completed` event is received.

### Lesson

Streaming output and successful completion are two different things.

An application should not assume that receiving partial streamed text means the entire request succeeded. The final completion or error event must also be handled.

### Additional Observation

The high-demand error did not occur during testing on the following day, even though the code had not changed.

This showed that API behaviour can vary between requests and over time because of temporary service conditions.

## 4. Daily API Request Quota

### Issue

During testing, the Gemini API eventually returned a `rate_limit_exceeded` error because the account had reached its daily request quota.

The error reported a limit of **20 requests per day on the Free Tier** at the time of testing.

```text id="f2e8yw"
rate_limit_exceeded:
Rate limit exceeded for model gemini-3.6-flash
(limit: 20 requests per day on Free Tier)
```

### What happened

The application already had retry logic for temporary API errors.

However, retrying is not useful when the **daily quota has been exhausted**, because making another request does not restore the available quota.

### Fix

I added a separate check for `rate_limit_exceeded` errors:

```python id="q9xw2n"
if "rate_limit_exceeded" in error_message.lower():
    print("\nYour daily Gemini API request limit has been reached.")
    return ""
```

This handles the daily quota separately from temporary errors such as service unavailability or temporary high demand.

Temporary errors can trigger the retry mechanism, while an exhausted daily quota results in a clear message to the user instead of unnecessary retries.

### Lesson

Not all temporary errors should be handled in the same way.

A temporary service problem may recover after waiting and can be retried, while an exhausted daily quota requires waiting for the quota to reset or changing the API usage tier.

## 5. Conversation Reset and Interaction ID

### Issue

The `/clear` command originally cleared the locally stored conversation messages only, but it did not reset the Gemini interaction ID.

The application therefore had two separate pieces of conversation state:

* **Local conversation history** stored in `ConversationManager` class
* **Gemini conversation continuity** stored through `previous_interaction_id`

Clearing only the local messages did not completely start a fresh Gemini conversation because the previous IDs were stored anyway.

### What happened

Even after the local conversation history was cleared, the previous interaction ID could still connect the next request to the earlier Gemini conversation.

This meant that the assistant could potentially retain context from previous turns even though the displayed conversation history was empty.

### Fix

I updated the conversation-clearing logic so that both pieces of state are reset:

```python id="h4x8qp"
def clear_conversation():
    global previous_interaction_id
    conversation.clear_history()
    previous_interaction_id = None
```

The `/clear` command now calls this function:

```python id="n7c3kw"
/clear → clear local history + reset interaction ID
```

This allows the next request to begin a fresh conversation.

### Lesson

Conversation history and conversation continuity are not necessarily the same thing.

An application can store its own local history while the API maintains separate state for connecting one interaction to the next. When implementing a "clear conversation" feature, both types of state need to be considered.

## Key Debugging Lessons

Working through these issues helped me understand several important aspects of developing an AI-powered application:

* **Separate the layers of a problem.** An API failure may come from the environment, authentication, model availability, API method, parameters, service conditions, or application logic.
* **Read errors carefully.** The error message and traceback often provide the most useful clue about where the problem occurred.
* **Do not assume partial success means complete success.** Receiving streamed text does not guarantee that the interaction completed successfully.
* **Handle different errors differently.** Temporary service errors may be retried, while an exhausted daily quota should not trigger unnecessary retries.
* **Track all relevant application state.** Clearing locally stored messages is not enough if the API maintains separate conversation continuity.
* **Test behaviour, not just code execution.** A chatbot can run without errors while still behaving incorrectly, such as forcing unrelated questions into its intended domain.
* **API behaviour can change over time.** Models, quotas, and service availability may change even when the application code remains unchanged.
* **Make targeted fixes.** Identifying the specific source