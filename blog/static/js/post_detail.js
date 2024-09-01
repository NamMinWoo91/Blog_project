document.addEventListener("DOMContentLoaded", function () {
    const commentsSection = document.querySelector(".comments-section");

    // 댓글 작성 및 수정
    commentsSection.addEventListener("submit", function (e) {
        if (
            e.target.matches("#comment-form") ||
            e.target.closest(".reply-form") ||
            e.target.closest(".edit-form")
        ) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);

            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        if (form.id === "comment-form") {
                            document
                                .getElementById("comments-list")
                                .insertAdjacentHTML("beforeend", data.html);
                        } else if (form.closest(".reply-form")) {
                            const parentComment = form.closest(".comment");
                            let repliesContainer =
                                parentComment.querySelector(".replies");
                            if (!repliesContainer) {
                                repliesContainer =
                                    document.createElement("div");
                                repliesContainer.className = "replies";
                                parentComment.appendChild(repliesContainer);
                            }
                            repliesContainer.insertAdjacentHTML(
                                "beforeend",
                                data.html
                            );
                        } else if (form.closest(".edit-form")) {
                            const commentDiv = form.closest(".comment");
                            commentDiv.querySelector(
                                ".comment-content"
                            ).textContent = data.content;
                            form.closest(".edit-form").style.display = "none";
                            commentDiv.querySelector(
                                ".comment-content"
                            ).style.display = "block";
                        }
                        form.reset();
                        if (form.closest(".reply-form")) {
                            form.closest(".reply-form").style.display = "none";
                        }
                    } else {
                        throw new Error(JSON.stringify(data.errors));
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    let errorMessage = "댓글 처리 중 오류가 발생했습니다.";
                    try {
                        const errorData = JSON.parse(error.message);
                        errorMessage +=
                            " " + Object.values(errorData).flat().join("\n");
                    } catch {
                        errorMessage += " " + error.message;
                    }
                    alert(errorMessage);
                });
        }
    });

    // 답글 폼 토글
    commentsSection.addEventListener("click", function (e) {
        if (e.target.matches(".reply-button")) {
            const commentId = e.target.dataset.commentId;
            const replyForm = document.getElementById(
                `reply-form-${commentId}`
            );
            replyForm.style.display =
                replyForm.style.display === "none" ? "block" : "none";
        }
    });

    // 댓글 수정 폼 토글
    commentsSection.addEventListener("click", function (e) {
        if (e.target.matches(".edit-comment")) {
            const commentId = e.target.dataset.commentId;
            const editForm = document.getElementById(`edit-form-${commentId}`);
            const commentContent = e.target
                .closest(".comment")
                .querySelector(".comment-content");
            editForm.style.display = "block";
            commentContent.style.display = "none";
        }
        if (e.target.matches(".cancel-edit")) {
            const editForm = e.target.closest(".edit-form");
            const commentContent = editForm.previousElementSibling;
            editForm.style.display = "none";
            commentContent.style.display = "block";
        }
    });

    // 댓글 삭제
    commentsSection.addEventListener("click", function (e) {
        if (e.target.matches(".delete-comment")) {
            e.preventDefault();
            if (confirm("정말 이 댓글을 삭제하시겠습니까?")) {
                const form = e.target.closest("form");
                fetch(form.action, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.success) {
                            e.target.closest(".comment").remove();
                        }
                    });
            }
        }
    });

    const likeButton = document.getElementById("like-button");
    if (likeButton) {
        likeButton.addEventListener("click", function () {
            const postId = this.dataset.postId;
            const likeCount = document.getElementById("like-count");

            fetch(`/blog/like/${postId}/`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "success") {
                        likeCount.textContent = data.likes_count;
                        this.textContent = data.is_liked
                            ? "좋아요 취소"
                            : "좋아요";
                        this.appendChild(likeCount);
                    }
                })
                .catch((error) => console.error("Error:", error));
        });
    }

    // 북마크 기능
    const bookmarkButton = document.getElementById("bookmark-button");
    if (bookmarkButton) {
        bookmarkButton.addEventListener("click", function () {
            const postId = this.dataset.postId;
            const bookmarkCount = document.getElementById("bookmark-count");

            fetch(`/blog/bookmark/${postId}/`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "success") {
                        bookmarkCount.textContent = data.bookmarks_count;
                        this.textContent = data.is_bookmarked
                            ? "북마크 취소"
                            : "북마크";
                        this.appendChild(bookmarkCount);
                    }
                })
                .catch((error) => console.error("Error:", error));
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }
});
