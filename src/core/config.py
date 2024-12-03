from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    # Application secret key and security settings
    # SECRET_KEY: str = os.getenv("SECRET_KEY")
    # ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    #     os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 600)
    # )

    # ----------Database configuration-----------
    # The DATABASE_URL variable will be loaded from the .env file
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # ----------API configuration----------------

    # OpenAI API configuration
    # openai_api_key: str = os.getenv("OPENAI_API_KEY")

    # # together.ai API key
    # together_api_key: str = os.getenv("TOGETHER_API_KEY")

    # # GitHub API key
    # github_api_key: str = os.getenv("GITHUB_API_KEY")

    # # Azure OpenAI API configuration
    # azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY")
    # azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    # azure_openai_deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    # ----------Email configuration--------------

    # ----------Selenium configuration-----------
  
    path_mac = os.getenv('driver_path_mac')
    path_windows = os.getenv('driver_path_win')
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    LINKS_PROGRESS_PATH = os.path.join(ROOT_DIR, 'links_progress.json')
    POSTS_COMMENTS_PATH = os.path.join(ROOT_DIR, 'posts_comments.json')
    fb_user = os.getenv('user')
    fb_password = os.getenv('password')


settings = Settings()
