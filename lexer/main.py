# main.py

from src.controllers.main_controller import run_app, test_full_pipeline, generate_lexer, generate_global_dfa
from src.models.mindfa import minimize_dfa, render_mindfa


if __name__ == "__main__":
    # test_full_pipeline("inputs/lexer.yal")
    # global_dfa = generate_global_dfa()
    # min_dfa = minimize_dfa(global_dfa)
    # render_mindfa(min_dfa, "global_dfa_minimized")
    generate_lexer()

    # run_app()