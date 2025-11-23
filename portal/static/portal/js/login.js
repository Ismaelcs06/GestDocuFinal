document.addEventListener("DOMContentLoaded", () => {
    const pwd = document.getElementById("id_password");
    const eye = document.getElementById("toggleEye");
    if (eye && pwd) {
        eye.addEventListener("click", () => {
            const isPwd = pwd.type === "password";
            pwd.type = isPwd ? "text" : "password";
            eye.textContent = isPwd ? "Ocultar" : "Mostrar";
        });
    }
});
