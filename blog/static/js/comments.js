document.addEventListener("DOMContentLoaded", function () {
    const replyButtons = document.querySelectorAll(".reply-button");

    replyButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(
                `reply-form-${commentId}`
            );
            replyForm.style.display =
                replyForm.style.display === "none" ? "block" : "none";
        });
    });
});
