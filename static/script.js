$(document).ready(function() {
    const passwordCriteria = {
        minLength: /(?=.{8,})/,
        uppercase: /(?=.*[A-Z])/,
        lowercase: /(?=.*[a-z])/,
        number: /(?=.*[0-9])/,
        symbol: /(?=.*[!@#$%^&*(),.?":{}|<>])/,
    };
    let isValid = {
        minLength: false,
        uppercase: false,
        lowercase: false,
        number: false,
        symbol: false,
    };
    function checkPassword() {
        const password = $("input[name='password']").val();
        isValid.minLength = passwordCriteria.minLength.test(password);
        isValid.uppercase = passwordCriteria.uppercase.test(password);
        isValid.lowercase = passwordCriteria.lowercase.test(password);
        isValid.number = passwordCriteria.number.test(password);
        isValid.symbol = passwordCriteria.symbol.test(password);
        $(".criteria").each(function() {
            const criteria = $(this).data("criteria");
            if (isValid[criteria]) {
                $(this).removeClass("unfulfilled").addClass("fulfilled");
            } else {
                $(this).removeClass("fulfilled").addClass("unfulfilled");
            }
        });
        if (Object.values(isValid).every(value => value)) {
            $("input[name='confirm_password']").prop("disabled", false);
        } else {
            $("input[name='confirm_password']").prop("disabled", true);
        }
    }
    $("input[name='password']").on("input", checkPassword);
});