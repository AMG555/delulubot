# RAG Data Folder

This folder contains knowledge files that define your bot's personality, lore, and behavior patterns using RAG (Retrieval-Augmented Generation).

## Creating Your Own Character

To personalize the bot with your own character:

1. **Character Bible** (`rag_data/delulu_character_bible.md`)
   - Define core personality traits, speech patterns, background
   - Example structure:
     ```markdown
     # Character Name
     Age: X | Gender: Y | Origin: Z
     
     ## Personality Core
     - Trait 1
     - Trait 2
     
     ## Speech Style
     - How they talk
     - Phrases they use
     
     ## Background
     - Their story
     ```

2. **Lore Document** (`rag_data/delulu_lore.md`)
   - Character's backstory, relationships, world details
   - Events that shaped them

3. **Conversation Patterns** (`rag_data/conversation_patterns.md`)
   - Example conversations showing your character's voice
   - How they respond to different situations

4. **Companion Playbook** (`rag_data/delulu_companion_playbook.md`)
   - Interaction guidelines
   - How character handles emotions, advice, humor

## Supported File Types
- `.md` (Markdown)
- `.txt` (Plain text)
- `.json` (Structured data)

## Usage

1. Create your character files in this folder
2. Update `CHARACTER_BIBLE_FILE` in `.env` to point to your main character file
3. Restart bot or run `/ragreload`
4. Check `/ragstatus` to verify files loaded
5. Test with `/ragsearch <query>`

## Tips

- Keep documents factual and concise
- Split very large docs into smaller topical files
- Add one file per topic for better retrieval quality
- Use specific examples of how your character talks
- Include edge cases (how they handle sadness, excitement, confusion)

## Testing Your Character

- `/ask <question>` - Test character responses
- `/mood` - Check emotional handling
- `/random` - See spontaneous character behavior
- `/sing` - Test creative responses

## Personal Memory System

- `/remember <fact>` - Store user-specific facts
- `/aboutme` - View what bot remembers about you
- `/forget` - Remove a saved fact
- `/companion` - Quick usage guide

