$(document).ready(function () {
    const commentActions = {
        init: function () {
            this.bindEditCommentEvents();
            this.bindReplyCommentEvents();
            this.bindDeleteCommentEvents();
            this.bindCancelEditEvent();
        },

        bindEditCommentEvents: function () {
            $(".edit-button").click(function () {
                const commentId = $(this).data("comment-id");
                const commentContent = $(this)
                    .siblings(".comment-content")
                    .text();
                const actionUrl = `/blog/comment/update/${commentId}/`;
                const csrfToken = $("[name=csrfmiddlewaretoken]").val();

                const editForm = `
                    <form class="edit-form" method="post" action="${actionUrl}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                        <textarea name="content">${commentContent}</textarea>
                        <button type="submit">수정하기</button>
                        <button type="button" class="cancel-edit">취소</button>
                    </form>
                `;

                $(`#comment-${commentId}`).html(editForm);
            });
        },

        bindReplyCommentEvents: function () {
            $(".reply-button").click(function () {
                const commentId = $(this).data("comment-id");
                $(`#reply-form-${commentId}`).toggle();
            });
        },

        bindDeleteCommentEvents: function () {
            $(".delete-button").click(function () {
                const commentId = $(this).data("comment-id");
                if (confirm("정말 삭제하시겠습니까?")) {
                    const deleteUrl = `/blog/comment/delete/${commentId}/`;
                    window.location.href = deleteUrl;
                }
            });
        },

        bindCancelEditEvent: function () {
            $(document).on("click", ".cancel-edit", function () {
                location.reload();
            });
        },
    };

    const postInteractions = {
        init: function () {
            this.bindLikeEvent();
            this.bindBookmarkEvent();
        },

        bindLikeEvent: function () {
            $("#like-button").click(function () {
                const postId = $(this).data("post-id");
                $.ajax({
                    url: `/blog/like/${postId}/`,
                    type: "POST",
                    data: {
                        csrfmiddlewaretoken: $(
                            "[name=csrfmiddlewaretoken]"
                        ).val(),
                    },
                    success: function (response) {
                        $("#like-button").text(
                            response.liked ? "좋아요 취소" : "좋아요"
                        );
                        $("#like-count").text(response.total_likes);
                    },
                    error: function (xhr, status, error) {
                        console.error("좋아요 처리 중 오류 발생:", error);
                    },
                });
            });
        },

        bindBookmarkEvent: function () {
            $("#bookmark-button").click(function () {
                const postId = $(this).data("post-id");
                $.ajax({
                    url: `/blog/bookmark/${postId}/`,
                    type: "POST",
                    data: {
                        csrfmiddlewaretoken: $(
                            "[name=csrfmiddlewaretoken]"
                        ).val(),
                    },
                    success: function (response) {
                        $("#bookmark-button").text(
                            response.is_bookmarked ? "북마크 취소" : "북마크"
                        );
                        $("#bookmark-count").text(response.bookmark_count);
                    },
                    error: function (xhr, status, error) {
                        console.error("북마크 처리 중 오류 발생:", error);
                    },
                });
            });
        },
    };
    const commentForm = {
        init: function () {
            this.bindSubmitEvent();
        },

        bindSubmitEvent: function () {
            $("#comment-form").on("submit", function (e) {
                e.preventDefault();
                const form = $(this);
                const url = form.attr("action");
                const formData = form.serialize();

                $.ajax({
                    url: url,
                    type: "POST",
                    data: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    success: function (response) {
                        // 새 댓글을 페이지에 추가
                        $(".comments-section").append(response.html);
                        form.find("textarea").val(""); // 폼 초기화
                    },
                    error: function (xhr, status, error) {
                        console.error("댓글 작성 중 오류 발생:", error);
                        alert("댓글 작성에 실패했습니다. 다시 시도해 주세요.");
                    },
                });
            });
        },
    };
    // 초기화
    commentActions.init();
    postInteractions.init();
    commentForm.init();
});
