
   //Показване и скриване на менюто при мобилен изглед
    function showMenu() {
        const navLinks = document.getElementById('navLinks');
        navLinks.classList.toggle('show');
    }
    const modal = document.getElementById("modal");
    const openModalBtn = document.getElementById("details");
    const closeModalBtn = document.querySelector(".close");


    //РЕГИСТРАЦИЯ И ВАРИФИКАЦИЯ НА ВЪВЕДЕНИТЕ ДАННИ
    const profileImageInput = document.getElementById('profileImage');
    const profilePreview = document.getElementById('profilePreview');
                          
    // Събитие за промяна на избора на файл
    profileImageInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        profilePreview.src = e.target.result;
    };
    reader.readAsDataURL(file);
    });
    function ensurePrefix() {
        const prefix = '+359';
        const phoneField = document.getElementById('phoneField');
        // Ако полето е празно при фокус, добавяме +359
        if (!phoneField.value) {
            phoneField.value = prefix;
            }
        }
                          
                            function limitDigits(event) {
                              const prefix = '+359';
                              let val = event.target.value;
                          
                              // Ако някой опита да изтрие prefix-а или да въведе нещо друго отпред,
                              // насилствено го коригираме да започва с +359
                              if (!val.startsWith(prefix)) {
                                // Премахваме всички нецифрови символи
                                val = val.replace(/\D/g, '');
                                // Добавяме prefix
                                val = prefix + val;
                              }
                          
                              // Обрязваме всякакви други знаци след +359
                              let rest = val.slice(prefix.length);
                              // Разрешаваме само цифри
                              rest = rest.replace(/\D/g, '');
                              // Ограничава до 9 цифри
                              rest = rest.slice(0, 9);
                          
                              // Сглобяваме обратно
                              val = prefix + rest;
                              event.target.value = val;
                            }
                            const cityInput = document.getElementById('city');
                                const postalCodeInput = document.getElementById('postalCode');
                                const cityError = document.getElementById('city-error');
                                const postalError = document.getElementById('postal-error');

                                // Позволени символи за "Град" – само кирилица, интервал, точка и тире
                                cityInput.addEventListener('input', function () {
                                    const regex = /^[А-Яа-яЁё -.]+$/;
                                    if (!regex.test(cityInput.value) && cityInput.value !== "") {
                                        cityError.style.display = 'block';
                                        cityInput.value = cityInput.value.replace(/[^А-Яа-яЁё -.]/g, '');
                                    } else {
                                        cityError.style.display = 'none';
                                    }
                                });

                                // Ограничение за "Пощенски код" – само 4 цифри
                                postalCodeInput.addEventListener('input', function () {
                                    postalCodeInput.value = postalCodeInput.value.replace(/\D/g, '').substring(0, 4);
                                    if (postalCodeInput.value.length === 4) {
                                        postalError.style.display = 'none';
                                    } else {
                                        postalError.style.display = 'block';
                                    }
                                });
                                const passwordField = document.getElementById('password');
                            const confirmPasswordField = document.getElementById('confirmPassword');
                            const errorMessage = document.getElementById('error-message');
                            const passwordStrengthMessage = document.getElementById('password-strength');
                            const togglePassword = document.getElementById('togglePassword');
                          
                            // Регулярно изражение за силата на паролата
                            const strongPasswordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
                          
                            // Функция за проверка дали паролите съвпадат
                            function validatePasswords() {
                              if (passwordField.value !== confirmPasswordField.value) {
                                errorMessage.style.display = 'block';
                                confirmPasswordField.setCustomValidity("Паролите не съвпадат/n Над 8 символа, Една цифра и един специален знак ");
                              } else {
                                errorMessage.style.display = 'none';
                                confirmPasswordField.setCustomValidity("");
                              }
                            }
                          
                            // Функция за проверка на силата на паролата
                            function validatePasswordStrength() {
                              if (passwordField.value.length > 0 && !strongPasswordRegex.test(passwordField.value)) {
                                passwordStrengthMessage.style.display = 'block';
                              } else {
                                passwordStrengthMessage.style.display = 'none';
                              }
                            }
                          
                            // Функция за показване/скриване на паролата
                            togglePassword.addEventListener('click', function() {
                              const type = passwordField.type === 'password' ? 'text' : 'password';
                              passwordField.type = type;
                              confirmPasswordField.type = type;
                              togglePassword.textContent = type === 'password' ? '👁️' : '🙈';
                            });
                          
                            // Слушатели за събития за проверка на паролите
                            passwordField.addEventListener('input', function() {
                              validatePasswords();
                              validatePasswordStrength();
                            });
                          
                            confirmPasswordField.addEventListener('input', validatePasswords);
                            function showLogin() {
                    let loginForm = document.getElementById("login");
                    let registerForm = document.getElementById("register");
            
                    registerForm.style.opacity = "0";
                    setTimeout(() => {
                        registerForm.style.display = "none";
                        loginForm.style.display = "block";
                        setTimeout(() => loginForm.style.opacity = "1", 100);
                    }, 300);
                }
            
                function showRegister() {
                    let loginForm = document.getElementById("login");
                    let registerForm = document.getElementById("register");
            
                    loginForm.style.opacity = "0";
                    setTimeout(() => {
                        loginForm.style.display = "none";
                        registerForm.style.display = "block";
                        setTimeout(() => registerForm.style.opacity = "1", 100);
                    }, 300);
                }
            
                window.onload = function() {
                    document.getElementById("login").style.display = "block";
                    document.getElementById("register").style.display = "none";
                };

                function previewImage(event) {
                    const reader = new FileReader();
                    reader.onload = function () {
                        const img = document.getElementById('profilePreview');
                        img.src = reader.result;
                    }
                    reader.readAsDataURL(event.target.files[0]);
                }


    // Отваряне на модала при натискане на бутона
    openModalBtn.addEventListener("click", () => {
        modal.style.display = "flex";
    });

    // Затваряне на модала при натискане на (X)
    closeModalBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Затваряне на модала при клик извън съдържанието
    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
//ОТВАРЯНЕ И ЗАТВАРЯНЕ НА ШАБЛОНА ЗА ДОБАВЯНЕ НА ЖИВОТНО
            function openModal() {
                document.getElementById('myModal').style.display = "block";
            }
            function closeModal() {
                document.getElementById('myModal').style.display = "none";
            }
            function updateType() {
                document.getElementById('typeInput').value = document.querySelector('input[name="Type"]:checked').value;
            }
            function toggleUnderOneYear() {
                const ageInput = document.getElementById('ageInput');
                ageInput.disabled = document.getElementById('underOneYear').checked;
                ageInput.value = ageInput.disabled ? 0 : '';
            }
            function validateNumberInput(input) {
                input.value = input.value.replace(/[^0-9]/g, '');
            }
            function clearForm() {
                document.querySelectorAll(".input-field").forEach(input => input.value = "");
                document.querySelectorAll("input[type='radio'], input[type='checkbox']").forEach(input => input.checked = false);
            }
            
            // Отваряне и затваряне на потвърдителния модал
            function openConfirmModal() {
                document.getElementById('confirmModal').style.display = "block";
            }

            function closeConfirmModal() {
                document.getElementById('confirmModal').style.display = "none";
            }

            function submitForm() {
                closeConfirmModal();
                alert("Обявата беше успешно публикувана! 🎉");
                document.getElementById("petForm").submit();
            }

            function validateEditForm(data) {
                // ВИД
                if (!data.type_name || !['Куче', 'Котка', 'Птица', 'Хамстер', 'Друго'].includes(data.type_name)) {
                    alert('Моля, изберете валиден вид животно');
                    return false;
                }

                // ПОРОДА
                if (!data.breed_name || data.breed_name.trim() === '') {
                    alert('Моля, въведете порода');
                    return false;
                }

                // ГОДИНИ
                const age = parseInt(data.age);
                if (isNaN(age) || age < 0) {
                    alert('Моля, въведете валидна възраст');
                    return false;
                }

                // ЦЕНА
                const price = parseFloat(data.price);
                if (isNaN(price) || price < 0) {
                    alert('Моля, въведете валидна цена');
                    return false;
                }

                // ПОЛ
                if (!data.gender || !['мъжки', 'женски'].includes(data.gender)) {
                    alert('Моля, изберете валиден пол');
                    return false;
                }

                // ВАКСИНАЦИЯ
                if (!data.vaccinated || !['да', 'не'].includes(data.vaccinated)) {
                    alert('Моля, изберете валиден статус на ваксинация');
                    return false;
                }

                // ОПИСАНИЕ
                if (!data.description || data.description.trim() === '') {
                    alert('Моля, въведете описание');
                    return false;
                }

                return true;
            }

            // РЕДАКТИРАНЕ НА ДАННИТЕ НА ОБЯВИТЕ 
            function editAd(button) {
                const adItem = button.closest('.ad-item');
                const spans = adItem.querySelectorAll('.edit-text');
                
                spans.forEach(span => {
                    const value = span.textContent.trim();
                    const field = span.getAttribute('data-field');
                    let input;

                    if (field === 'type_name') {
                        input = document.createElement('select');
                        ['Куче', 'Котка', 'Птица', 'Хамстер', 'Друго'].forEach(type => {
                            const option = document.createElement('option');
                            option.value = type;
                            option.textContent = type;
                            if (type === value) option.selected = true;
                            input.appendChild(option);
                        });
                    } else if (field === 'gender') {
                        input = document.createElement('select');
                        ['мъжки', 'женски'].forEach(gender => {
                            const option = document.createElement('option');
                            option.value = gender;
                            option.textContent = gender;
                            if (gender === value) option.selected = true;
                            input.appendChild(option);
                        });
                    } else if (field === 'vaccinated') {
                        input = document.createElement('select');
                        ['да', 'не'].forEach(status => {
                            const option = document.createElement('option');
                            option.value = status;
                            option.textContent = status;
                            if (status === value) option.selected = true;
                            input.appendChild(option);
                        });
                    } else if (field === 'age') {
                        input = document.createElement('input');
                        input.type = 'number';
                        input.min = '0';
                        input.value = value.replace(/[^0-9]/g, '');
                    } else if (field === 'price') {
                        input = document.createElement('input');
                        input.type = 'number';
                        input.min = '0';
                        input.value = value.replace(/[^0-9.]/g, '');
                    } else {
                        input = document.createElement('input');
                        input.type = 'text';
                        input.value = value;
                    }

                    input.className = 'edit-input';
                    input.setAttribute('data-field', field);
                    span.replaceWith(input);
                });

                button.classList.add('hidden');
                adItem.querySelector('.save-ad').classList.remove('hidden');
            }

            // ЗАПАЗВАНЕ НА НОВИТЕ ДАННИ
            function saveAd(button) {
                const adItem = button.closest('.ad-item');
                const petId = button.getAttribute('data-id');
                const inputs = adItem.querySelectorAll('.edit-input');
                
                const data = {};
                inputs.forEach(input => {
                    const field = input.getAttribute('data-field');
                    data[field] = input.value.trim();
                });

                // Validate the form data
                if (!validateEditForm(data)) {
                    return;
                }

                fetch(`/pets/update/${petId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert(data.message);
                        location.reload();
                    } else {
                        alert(data.error || 'Грешка при запазване');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Грешка при запазване');
                });
            }

            // ИЗТРИВАНЕ НА ОБЯВА
            function deleteAd(button) {
                if (!confirm('Сигурни ли сте, че искате да изтриете тази обява?')) {
                    return;
                }

                const petId = button.getAttribute('data-id');
                
                fetch(`/ads/delete/${petId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert(data.message);
                        button.closest('.ad-item-form').remove();
                        location.reload();
                    } else {
                        alert(data.error || 'Грешка при изтриване');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Грешка при изтриване');
                });
            }
            window.onclick = function(event) {
                const modal = document.getElementById('myModal');
                const confirmModal = document.getElementById('confirmModal');
                if (event.target === modal) {
                    modal.style.display = "none";
                }
                if (event.target === confirmModal) {
                    confirmModal.style.display = "none";
                }
            }

            document.addEventListener('DOMContentLoaded', function() {
                const editBtn = document.getElementById('editProfileBtn');
                const saveBtn = document.getElementById('saveProfileBtn');
                const inputs = document.querySelectorAll('.profile-section .input-field');

                // Disable all inputs by default
                inputs.forEach(input => input.disabled = true);

                editBtn.addEventListener('click', function() {
                    inputs.forEach(input => input.disabled = false);
                    saveBtn.classList.remove('hidden');
                    editBtn.classList.add('hidden');
                });
            });
        
        