document.addEventListener('DOMContentLoaded',function(){const currentPasswordInput=document.getElementById('current_password');const newPasswordInput=document.getElementById('new_password');const showCurrentPasswordButton=document.getElementById('show_current_password');const showNewPasswordButton=document.getElementById('show_new_password');showCurrentPasswordButton.addEventListener('click',function(){togglePasswordVisibility(currentPasswordInput,showCurrentPasswordButton);});showNewPasswordButton.addEventListener('click',function(){togglePasswordVisibility(newPasswordInput,showNewPasswordButton);});function togglePasswordVisibility(input,button){const type=input.getAttribute('type')==='password'?'text':'password';input.setAttribute('type',type);toggleEyeIcon(button,type);}
function toggleEyeIcon(button,type){const eyeIcon=button.querySelector('svg');if(type==='password'){eyeIcon.innerHTML=`
                <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 14">
                    <g stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                      <path d="M10 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
                      <path d="M10 13c4.97 0 9-2.686 9-6s-4.03-6-9-6-9 2.686-9 6 4.03 6 9 6Z"/>
                    </g>
                </svg>
                `;}else{eyeIcon.innerHTML=`
                <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 18">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1.933 10.909A4.357 4.357 0 0 1 1 9c0-1 4-6 9-6m7.6 3.8A5.068 5.068 0 0 1 19 9c0 1-3 6-9 6-.314 0-.62-.014-.918-.04M2 17 18 1m-5 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
                </svg>
                `;}}});;