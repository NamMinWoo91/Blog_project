document.addEventListener("DOMContentLoaded", function () {
    const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
    ).value;

    // 좋아요 기능
    const likeButton = document.getElementById("like-button");
    if (likeButton) {
        likeButton.addEventListener("click", function (e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            fetch(`/blog/like/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json",
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    document.getElementById("like-count").textContent =
                        data.total_likes;
                    this.textContent = data.liked ? "좋아요 취소" : "좋아요";
                });
        });
    }

    // 북마크 기능
    const bookmarkButton = document.getElementById("bookmark-button");
    if (bookmarkButton) {
        bookmarkButton.addEventListener("click", function (e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            fetch(`/blog/bookmark/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json",
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    document.getElementById("bookmark-count").textContent =
                        data.bookmark_count;
                    this.textContent = data.is_bookmarked
                        ? "북마크 취소"
                        : "북마크";
                });
        });
    }

    // 북마크된 게시물 목록 (옵션)
    const bookmarkedPostsButton = document.getElementById(
        "bookmarked-posts-button"
    );
    if (bookmarkedPostsButton) {
        bookmarkedPostsButton.addEventListener("click", function (e) {
            e.preventDefault();
            fetch("/blog/bookmarks/", {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    // 북마크된 게시물 목록을 표시하는 로직
                    const bookmarksList =
                        document.getElementById("bookmarks-list");
                    bookmarksList.innerHTML = "";
                    data.bookmarked_posts.forEach((post) => {
                        const li = document.createElement("li");
                        li.textContent = post.title;
                        bookmarksList.appendChild(li);
                    });
                });
        });
    }
});
