from pydantic import BaseModel


class GithubUserModel(BaseModel):
    name: str = None
    blog: str = None
    bio: str = None
    public_repos: int = 0
    followers: int = 0
    avatar_url: str = None