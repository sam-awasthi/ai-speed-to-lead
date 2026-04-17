# AI Speed-to-Lead

An AI assistant that responds to inbound leads within 60 seconds and handles the full qualification conversation.

## The Problem

Companies lose the majority of inbound leads because no human follows up fast enough. By the time someone calls back, the lead has moved on.

## What This Does

- A lead submits their details (name, postcode, property type)
- Within 60 seconds, an AI assistant named Alex sends a personalised message referencing their specific property and location
- Alex handles the entire conversation — answers questions, qualifies intent, and either converts them to self-serve signup or prepares a handoff brief for a human agent

## Tech Stack

- **Backend:** Python + Flask
- **AI:** Anthropic Claude API with dynamic prompt engineering
- **Frontend:** Vanilla HTML/CSS/JS

## Running Locally

1. Clone the repo
2. Install dependencies: `pip install flask anthropic`
3. Run: `python demo.py`
4. Open `http://localhost:5050` in your browser
5. Enter your Anthropic API key in the demo interface
