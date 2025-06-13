from django.shortcuts import render
from django.http import JsonResponse
from django.http.response import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from .models import chat_logs

import urllib.parse
import urllib.request

import json

client = OpenAI(base_url="http://192.168.1.6:1234/v1", api_key="lm-studio")


def get_or_create_anonymous_user(request):
    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key

    messages = chat_logs.objects.get_or_create(session_key=session_key)

    return messages


def serialize(obj):
    # Detect OpenAI's Function object by attribute presence
    if hasattr(obj, "arguments") and hasattr(obj, "name"):
        return {"arguments": obj.arguments, "name": obj.name}
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    else:
        return obj


def fetch_wikipedia_content(search_query: str) -> dict:
    try:
        # Search for most relevant article
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_query,
            "srlimit": 1,
        }

        url = f"{search_url}?{urllib.parse.urlencode(search_params)}"
        with urllib.request.urlopen(url) as response:
            search_data = json.loads(response.read().decode())

        if not search_data["query"]["search"]:
            return {
                "status": "error",
                "message": f"No Wikipedia article found for '{search_query}'",
            }

        # Get the normalized title from search results
        normalized_title = search_data["query"]["search"][0]["title"]

        # Now fetch the actual content with the normalized title
        content_params = {
            "action": "query",
            "format": "json",
            "titles": normalized_title,
            "prop": "extracts",
            "exintro": "true",
            "explaintext": "true",
            "redirects": 1,
        }

        url = f"{search_url}?{urllib.parse.urlencode(content_params)}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]

        if page_id == "-1":
            return {
                "status": "error",
                "message": f"No Wikipedia article found for '{search_query}'",
            }

        content = pages[page_id]["extract"].strip()
        print(
            {
                "status": "success",
                "content": content,
                "title": pages[page_id]["title"],
            }
        )
        return {
            "status": "success",
            "content": content,
            "title": pages[page_id]["title"],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# Define tool for LM Studiofunc
wiki_tool = {
    "type": "function",
    "function": {
        "name": "fetch_wikipedia_content",
        "description": (
            "Search Wikipedia and fetch the introduction of the most relevant article. "
            "If the user has a typo in their search query, correct it before searching."
            "Use it only if you need it.keep the use of it to minimal.                 "
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Search query for finding the Wikipedia article",
                },
            },
            "required": ["search_query"],
        },
    },
}


# Create your views here.
def index(request):
    request.session.flush()
    request.session.save()
    return render(request, "chatai/main.html")


def completions(request):
    print("gotcha!!!")

    if request.method == "POST":
        body = json.loads(request.body)
        sys_prompt = body.get("sys_prompt", "")
        usesrinput = body.get("userIn", "")

    session_key_now = request.session.session_key
    if not chat_logs.objects.filter(session_key=session_key_now).exists():
        chat_logs.objects.create(
            session_key=session_key_now,
            messages=sys_prompt,
        )
    """else:
        chat = chat_logs.objects.get(session_key=session_key_now).messages
        chat.append({"role": "user", "content": usesrinput})"""

    chat = chat_logs.objects.get(session_key=session_key_now).messages
    chat.append({"role": "user", "content": usesrinput})

    completion = client.chat.completions.create(
        model="llama-3.1-8b-lexi-uncensored-v2",
        messages=chat,
        tools=[wiki_tool],
        function_call="auto",
    )
    if completion.choices[0].finish_reason == "tool_calls":
        tool_calls = completion.choices[0].message.tool_calls
        print("tool call baybyyy")
        chat.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": tool_call.function,
                    }
                    for tool_call in tool_calls
                ],
            }
        )
        for tool_call in tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = fetch_wikipedia_content(args["search_query"])

            chat.append(
                {
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                }
            )

        chat.append(
            {"role": "assistant", "content": completion.choices[0].message.content}
        )

        chat_logs.objects.filter(session_key=session_key_now).update(
            messages=serialize(chat)
        )

        return streaming_response(chat, session_key_now)

    else:
        chat.append(
            {
                "role": "assistant",
                "content": completion.choices[0].message.content,
            }
        )

        return streaming_response(chat, session_key_now)


def chunk_response(chat, session_key_now):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-lexi-uncensored-v2",
        messages=chat,
        stream=True,
    )

    full_response = ""

    for chunk in completion:
        content = chunk.choices[0].delta.content
        if content is not None:
            full_response += content
            yield content
    chat.append({"role": "assistant", "content": full_response})
    chat = serialize(chat)
    chat_logs.objects.filter(session_key=session_key_now).update(messages=chat)


def streaming_response(chat, session_key_now):
    response = StreamingHttpResponse(
        chunk_response(chat, session_key_now), status=200, content_type="text/plain"
    )
    return response
