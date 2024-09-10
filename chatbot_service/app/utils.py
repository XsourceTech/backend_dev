from database_sharing_service.app import schemas


levels_dict = {}
levels_dict["article"] = ['major', 'field', 'topic', 'title', 'end']

def get_current_level(bot_memory: schemas.BotMemory, part: str):
    levels = levels_dict[part]
    current_index = 0
    current_rounds = 0
    for chat_message in bot_memory:
        if current_index >= len(levels) - 1:
            break
        if chat_message['role'] == 'user':
            current_rounds += 1
        elif chat_message['role'] == 'assistant':
            if "谢谢你的回答。我了解了" in chat_message['content'] or "再次感谢你的回答" in chat_message['content']:
                current_index += 1
                current_rounds = 0
            elif current_rounds >= 4:
                current_index += 1
                current_rounds = 0
    return levels[current_index]