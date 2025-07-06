# Feed App

A Django-based feed application with intelligent post scoring and recommendation system.

## Features

- **User Profiles**: Extended user profiles with primary and secondary interests
- **Post Management**: Posts with images, text, and interest tags
- **Smart Scoring**: Configurable relevance weights for post scoring
- **Seen Tracking**: Track which users have seen which posts
- **Admin Interface**: Full Django admin integration for all models

## Models

### Core Models
- **Interest**: Tags like "music", "sports", etc.
- **UserProfile**: Extended user profile with interest preferences
- **Post**: Posts with images, text, and tags
- **SeenPost**: Track post views by users
- **RelevanceWeight**: Configurable weights for scoring algorithm

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Set up default weights**:
   ```bash
   python manage.py setup_default_weights
   ```

5. **Generate sample data**:
   ```bash
   python manage.py generate_posts --count 150
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## Management Commands

### Generate Posts
Generate random posts with images and text:

```bash
# Generate 150 posts (default)
python manage.py generate_posts

# Generate specific number of posts
python manage.py generate_posts --count 200

# Use Unsplash API (requires API key)
python manage.py generate_posts --count 100 --unsplash-key YOUR_API_KEY
```

**Features**:
- Fetches random images from Lorem Picsum (or Unsplash with API key)
- Creates posts with random inspirational text
- Assigns 1-3 random interest tags per post
- Varies post creation times (up to 30 days ago)
- Creates 50+ different interest categories

### Setup Default Weights
Initialize default relevance weights for scoring:

```bash
python manage.py setup_default_weights
```

**Default Weights**:
- Primary tag weight: 1.0
- Secondary tag weight: 0.5
- Freshness weight: 0.3
- Seen penalty: 0.1

## Admin Interface

Access the admin interface at `/admin/` to manage:

- **Interests**: Create and manage interest tags
- **User Profiles**: View and edit user interest preferences
- **Posts**: Manage posts, images, and tags
- **Seen Posts**: Track post view history
- **Relevance Weights**: Configure scoring algorithm weights

## API Endpoints

The app includes Django REST Framework for API access:

### User Registration
**POST** `/api/register/`
- Register a new user with interests
- **Request Body:**
  ```json
  {
    "username": "newuser",
    "email": "user@example.com", 
    "password": "securepassword",
    "primary_interests": [1, 2, 3],
    "secondary_interests": [4, 5]
  }
  ```
- **Response:**
  ```json
  {
    "message": "User registered successfully!",
    "user": {
      "id": 1,
      "username": "newuser",
      "email": "user@example.com",
      "primary_interests": [...],
      "secondary_interests": [...]
    }
  }
  ```

### User Login
**POST** `/api/login/`
- Obtain an authentication token for a user
- **Request Body:**
  ```json
  {
    "username": "yourusername",
    "password": "yourpassword"
  }
  ```
- **Response:**
  ```json
  {
    "token": "yourauthtoken",
    "user": {
      "id": 1,
      "username": "yourusername",
      "email": "user@example.com",
    }
  }
  ```
- Use the token in the `Authorization` header for authenticated requests:
  ```
  Authorization: Token yourauthtoken
  ```

### Personalized Feed
**GET** `/api/feed/`
- Get personalized posts sorted by relevance score
- **Authentication:** Required
- **Query Parameters:**
  - `page` (optional): Page number (default: 1)
  - `page_size` (optional): Posts per page, max 100 (default: 20)
- **Response:**
  ```json
  {
    "posts": [
      {
        "id": 1,
        "text": "Post content...",
        "image": "/media/posts/image.jpg",
        "tags": [...],
        "created_at": "2025-07-06T10:00:00Z",
        "score": 85.5
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_posts": 150,
      "total_pages": 8,
      "has_next": true,
      "has_previous": false
    }
  }
  ```

### Mark Post as Seen
**POST** `/api/posts/<id>/seen/`
- Mark a specific post as seen by the authenticated user
- **Authentication:** Required
- **URL Parameters:**
  - `id`: Post ID to mark as seen
- **Response:**
  ```json
  {
    "message": "Post 1 marked as seen",
    "post_id": 1
  }
  ```

### List Available Interests
**Management Command:** `python manage.py list_interests`
- Lists all available interests with their IDs for registration

### Performance Testing
**Management Command:** `python manage.py test_feed_performance`
- Test the performance of optimized feed generation
- **Options:**
  - `--user-id`: Test specific user
  - `--page-size`: Set page size for testing (default: 20)
  - `--iterations`: Number of test iterations (default: 3)

## Scoring Algorithm

The post scoring system uses configurable weights:

1. **Interest Matching**: Posts matching user's primary interests get higher scores
2. **Secondary Interests**: Posts matching secondary interests get moderate scores
3. **Freshness**: Newer posts receive bonus points
4. **Seen Penalty**: Previously seen posts are deprioritized

Weights can be adjusted through the admin interface or programmatically.

## Performance Optimizations

The feed system is optimized for scalability with 100k+ posts and users:

### Database Optimizations
- **Select Related**: Reduces queries for related objects
- **Prefetch Related**: Efficiently loads many-to-many relationships
- **Batch Processing**: Calculates scores for multiple posts at once
- **Pagination**: Limits data transfer and memory usage

### Caching Strategy
- **Feed Caching**: User feeds cached for 5 minutes
- **Cache Invalidation**: Automatic cache clearing when posts are marked as seen
- **Configurable TTL**: Cache timeout can be adjusted in settings

### Query Optimization
- **N+1 Prevention**: Uses `select_related` and `prefetch_related`
- **Efficient Filtering**: Pre-filters seen posts and interests
- **Batch Scoring**: Calculates scores in memory after data is loaded

### Scalability Features
- **Pagination**: Supports large datasets with configurable page sizes
- **Memory Efficient**: Processes posts in batches
- **Cache Warming**: Can pre-warm caches for active users

## File Structure

```
feed-app/
├── core/                 # Django project settings
├── feed_app/            # Main application
│   ├── models.py        # Database models
│   ├── admin.py         # Admin interface
│   ├── management/      # Management commands
│   │   └── commands/
│   │       ├── generate_posts.py
│   │       └── setup_default_weights.py
│   └── migrations/      # Database migrations
├── media/               # User uploaded files
├── manage.py           # Django management script
└── README.md           # This file
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests if applicable
4. Submit a pull request

## License

This project is open source and available under the MIT License. 