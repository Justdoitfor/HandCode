import re
from typing import Callable


class ReActAgent:
    def __init__(
            self,
            llm: Callable[[list[dict]], str],
            tools: dict[str, Callable],
            max_steps: int = 5,
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def _build_system_prompt(self) -> str:
        tool_names = ", ".join(self.tools.keys())

        return f"""
你是一个 ReAct Agent。

可用工具：{tool_names}

请严格按照以下格式输出：

Thought: 思考过程
Action: 工具名称 或 Finish
Action Input: 工具输入

如果已经得到最终答案：

Thought: 已经得到答案
Action: Finish
Action Input: 最终答案

注意：
1. Action 必须是工具名称或者 Finish。
2. 如果需要工具，调用工具获取 Observation。
3. 获取 Observation 后继续思考。
""".strip()

    def parse(self, text: str) -> dict[str, str]:
        """解析 Thought、Action、Action Input"""

        result = {
            "thought": "",
            "action": "",
            "inp": "",
        }

        thought = re.search(
            r"Thought:\s*(.*?)(?=\nAction:)",
            text,
            re.DOTALL,
        )

        action = re.search(
            r"Action:\s*(.*?)(?=\nAction Input:)",
            text,
            re.DOTALL,
        )

        action_input = re.search(
            r"Action Input:\s*(.*)",
            text,
            re.DOTALL,
        )

        if thought:
            result["thought"] = thought.group(1).strip()

        if action:
            result["action"] = action.group(1).strip()

        if action_input:
            result["inp"] = action_input.group(1).strip()

        return result

    def run(self, question: str) -> str:
        messages = [
            {
                "role": "system",
                "content": self._build_system_prompt(),
            },
            {
                "role": "user",
                "content": question,
            },
        ]

        for _ in range(self.max_steps):
            print(messages)

            # 1. LLM 思考
            response = self.llm(messages)

            # 2. 解析
            result = self.parse(response)

            action = result["action"]
            action_input = result["inp"]

            # 3. 判断是否结束
            if action == "Finish":
                return action_input

            # 4. 调用工具
            if action not in self.tools:
                observation = f"UnknownToolError: {action}"
            else:
                try:
                    observation = self.tools[action](action_input)
                except Exception as e:
                    observation = f"ToolError: {e}"

            # 5. 将 Thought + Action 写回上下文
            messages.append({
                "role": "assistant",
                "content": response,
            })

            messages.append({
                "role": "tool",
                "content": f"Observation: {observation}",
            })

        return "Reach max steps, quit loop"


# mock llm
def mock_llm(messages: list[dict]) -> str:
    # 已经执行过工具
    if messages[-1]["content"].startswith("Observation:"):
        return """
Thought: 已经获得计算结果，可以返回最终答案
Action: Finish
Action Input: result is 65
"""

    # 第一轮
    return """
Thought: 需要计算 20 * 3 + 5
Action: calculator
Action Input: 20*3+5
"""


def cal(expression: str):
    return str(eval(expression))


if __name__ == "__main__":
    agent = ReActAgent(llm=mock_llm, tools={"calculator": cal})
    res = agent.run("calculate 20 * 3 + 5")
    print(res)
