import React, {useState} from 'react'
import api from '../api'
import '../CSS/register.css';

export const Register = () => {
    const [username, setUsername] = useState ('');
    const [password, setPassword] = useState ('');
    const [checkPassword, setCheckPassword] = useState('');
    const [email, setEmail] = useState('');
    const [admin, setAdmin] = useState (0);

    const handleInputChange = (event) => {
        const {name, value} = event.target;
        if(name==='username') setUsername(value);
        else if (name==='password') setPassword(value);
        else if (name==='checkPassword') setCheckPassword(value);
        else if (name==='email') setEmail(value);
        else if (name==='admin') setAdmin(perseInt(value,10));
    };

    const validateEmail=(email) => {
        const valid= /^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$/;
        return valid.test(email);
    };

    const displayMessage = (message) => {
        document.getElementById('info').innerHTML= message;
    };
    
    const handleFormSubmit = async(event) => {
        event.preventDefault();
        try{
            if(
                username.trim()===''||
                username.length>25 ||
                password.length<10 ||
                password !== checkPassword||
                !validateEmail(email)
            ) {
                if(username.trim()===''){
                    displayMessage('Username is blank');
                }
                else if(username.length > 25){
                    displayMessage('Username must be 25 character or less');
                }
                else if (!validateEmail(email)){
                    displayMessage('invalid email address');
                }
                else if (password.length < 10){
                    displayMessage('Password must be 10 character or longer');
                }
                else if (password !== checkPassword){
                    displayMessage ('Passwords do not match')
                }
            }
            else{
                const response = await api.post('/users/',{
                    username,
                    password,
                    email,
                    admin
                });
                if (repsponse.data.reponse==='Success'){
                    setUsername('');
                    setPassword('');
                    setCheckPassword('');
                    setEmail('');
                    setAdmin(0);
                    displayMessage('Account has been created successfully');
                }
                else if(response.data.response === 'Username taken'){
                    displayMessage('Username already exist');
                }
                else {
                    displayMessage('Server error')
                }
            }
        } catch (error){
            console.error('Error:', error);
            displayMessage('Error');
        }
    };

    return(

        <div className='wrap-register'>
            <div className={'register-form-box space-mono-bold'}>
                <h3>
                    Register
                </h3>
                <form onSubmit= {handleFormSubmit}>
                    <div className="input-box-register">
                        <span className="icon"><ion-icon name="mail"></ion-icon></span>
                        <input 
                            type='email'
                            name='email'
                            id='email'
                            required
                            onChange={handleInputChange}
                            value={email}
                        />
                        <label>Email</label>
                    </div>
                    <div className="input-box-register">
                        <span className="icon"><ion-icon name="person"></ion-icon> </span>
                        <input 
                            type='text'
                            name='username'
                            id='username'
                            required
                            onChange={handleInputChange}
                            value={username}
                        />
                        <label>Username</label>
                    </div>
                    <div className="input-box-register">
                        <span className="icon"><ion-icon name="lock-closed"></ion-icon></span>
                        <input 
                            type='password'
                            id='password'
                            name='password'
                            required
                            onChange={handleInputChange}
                            value={password}
                            
                        />
                        <label>Password</label>
                    </div>
                    <div className="input-box-register">
                        <span className="icon"><ion-icon name="lock-closed"></ion-icon></span>
                        <input 
                            type='password'
                            id='checkPassword'
                            name='checkPassword'
                            required
                            onChange={handleInputChange}
                            value={checkPassword}
                            
                        />
                        <label>Retype Password</label>
                    </div>
                    <button type = 'submit' className='bttn-register space-mono-bold'>Register</button>
                    <div className='account-login'><p>Already have an account? </p>
                        <a href="/#login"> Login</a>
                    </div>
                    <div id="info"></div>
                </form>
            </div>
        </div>
    )
};
export default Register;
