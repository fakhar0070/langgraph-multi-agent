import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from graph.workflow import build_graph

load_dotenv()

def run_cli():
    print("=" * 70)
    print("🤖 LangGraph Multi-Agent System (RAG + GitHub + Google Workspace)")
    print("=" * 70)
    print("Commands:")
    print(" - Type your query and press Enter.")
    print(" - Type 'exit' or 'quit' to close.\n")
    
    app = build_graph()
    
    while True:
        try:
            user_input = input("\nUser > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting. Khuda Hafiz!")
                break
                
            inputs = {"messages": [HumanMessage(content=user_input)]}
            print("\n[Agent is processing your request...]")
            
            final_output = None
            for event in app.stream(inputs, stream_mode="values"):
                final_output = event["messages"][-1]
                
            if final_output:
                print(f"\nAgent > {final_output.content}")
                
        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")

if __name__ == "__main__":
    run_cli()
