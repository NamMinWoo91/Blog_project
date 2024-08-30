document.addEventListener("DOMContentLoaded", function () {
    // 폼 및 제출 버튼 선택
    const form = document.querySelector(".post-form");
    const submitButton = form.querySelector('button[type="submit"]');

    // 폼 필드 선택
    const titleField = form.querySelector("#" + form.title.id_for_label);
    const contentField = form.querySelector("#" + form.content.id_for_label);
    const categoryField = form.querySelector("#" + form.category.id_for_label);
    const tagsField = form.querySelector("#" + form.tags.id_for_label);
    const headImageField = form.querySelector(
        "#" + form.head_image.id_for_label
    );
    const fileUploadField = form.querySelector(
        "#" + form.file_upload.id_for_label
    );

    // 에러 메시지를 표시할 함수
    function displayError(message) {
        const errorContainer = document.createElement("div");
        errorContainer.classList.add("error-messages");
        errorContainer.innerText = message;
        form.prepend(errorContainer);
    }

    // 폼 유효성 검사 함수
    function validateForm() {
        let isValid = true;
        let errorMessage = "";

        // 에러 메시지 컨테이너를 초기화
        const existingErrorContainer = form.querySelector(".error-messages");
        if (existingErrorContainer) {
            existingErrorContainer.remove();
        }

        // 제목 필드 검사
        if (titleField.value.trim() === "") {
            isValid = false;
            errorMessage += "제목을 입력해 주세요.\n";
        }

        // 내용 필드 검사
        if (contentField.value.trim() === "") {
            isValid = false;
            errorMessage += "내용을 입력해 주세요.\n";
        }

        // 카테고리 필드 검사
        if (categoryField.value.trim() === "") {
            isValid = false;
            errorMessage += "카테고리를 선택해 주세요.\n";
        }

        // 태그 필드 검사
        if (tagsField.value.trim() === "") {
            isValid = false;
            errorMessage += "태그를 입력해 주세요.\n";
        }

        // 파일 업로드 유효성 검사
        if (fileUploadField.files.length > 0) {
            const file = fileUploadField.files[0];
            if (file.size > 5 * 1024 * 1024) {
                // 5MB 제한
                isValid = false;
                errorMessage += "파일 크기는 5MB를 초과할 수 없습니다.\n";
            }
            const allowedExtensions = ["jpg", "jpeg", "png", "gif"];
            const fileExtension = file.name.split(".").pop().toLowerCase();
            if (!allowedExtensions.includes(fileExtension)) {
                isValid = false;
                errorMessage += "허용된 파일 형식: jpg, jpeg, png, gif.\n";
            }
        }

        // 에러 메시지 표시
        if (!isValid) {
            displayError(errorMessage);
        }

        return isValid;
    }

    // 폼 제출 시 유효성 검사
    form.addEventListener("submit", function (e) {
        if (!validateForm()) {
            e.preventDefault(); // 유효성 검사 실패 시 제출 방지
        }
    });
});
