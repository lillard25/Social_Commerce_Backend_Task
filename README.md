# Social Media API

A simple Django-based social media platform API that allows users to create posts, follow/unfollow other users, hide or block users, and view feeds filtered by their follow relationships.

## Requirements

- Python 3.8 or higher
- PostgreSQL

## Models

### User
- Uses Django's built-in `User` model for authentication and user management.

### Post
- `author` (ForeignKey to User): The creator of the post.
- `content` (Text): The text of the post (max length: 280 characters).
- `created_at` (DateTime): Timestamp of when the post was created.

### Follower
- `follower` (ForeignKey to User): The user who follows someone.
- `following` (ForeignKey to User): The user being followed.
- **Unique Constraint**: Prevent duplicate follow relationships.

### UserAction (For Hide and Block)
- `user` (ForeignKey to User): The user performing the action.
- `target_user` (ForeignKey to User): The user being hidden/blocked.
- `action` (ChoiceField): Possible choices are `HIDE` or `BLOCK`.
- **Unique Constraint**: Prevent duplicate actions for the same user-target pair.

