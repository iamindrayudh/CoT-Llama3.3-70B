from setuptools import setup, find_packages

setup(
    name="llama-cot-groq",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "groq>=0.4.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.4.2",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Chain of Thought implementation with Llama 3.3 70B using Groq API",
    keywords="llama, groq, chain-of-thought, reasoning, llm",
    python_requires=">=3.8",
)
