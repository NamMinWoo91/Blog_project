$(document).ready(function () {
    // 댓글 수정 버튼 클릭 이벤트
    $(".edit-button").click(function () {
        var commentId = $(this).data("comment-id");
        var commentContent = $(this).siblings(".comment-content").text();
        var actionUrl = "/blog/comment/update/" + commentId + "/";

        var csrfToken = $("[name=csrfmiddlewaretoken]").val();
        var editForm =
            `<form class="edit-form" method="post" action="${actionUrl}">` +
            `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">` +
            `<textarea name="content">${commentContent}</textarea>` +
            `<button type="submit">수정하기</button>` +
            `<button type="button" class="cancel-edit">취소</button>` +
            `</form>`;

        $("#comment-" + commentId).html(editForm);
    });

    // 대댓글 버튼 클릭 이벤트
    $(".reply-button").click(function () {
        var commentId = $(this).data("comment-id");
        $("#reply-form-" + commentId).toggle();
    });

    // 댓글 삭제 버튼 클릭 이벤트
    $(".delete-button").click(function () {
        var commentId = $(this).data("comment-id");
        if (confirm("정말 삭제하시겠습니까?")) {
            var deleteUrl = "/blog/comment/delete/" + commentId + "/";
            window.location.href = deleteUrl;
        }
    });

    // 댓글 수정 취소 버튼 클릭 이벤트
    $(document).on("click", ".cancel-edit", function () {
        location.reload();
    });

    // 좋아요 버튼 클릭 이벤트
    $("#like-button").click(function () {
        var postId = $(this).data("post-id");
        $.ajax({
            url: "/blog/like/" + postId + "/",
            type: "POST",
            data: {
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
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
});

$(document).ready(function () {
    // 기존 코드 유지...

    // 북마크 버튼 클릭 이벤트
    $("#bookmark-button").click(function () {
        var postId = $(this).data("post-id");
        $.ajax({
            url: "/blog/bookmark/" + postId + "/",
            type: "POST",
            data: {
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
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
});
