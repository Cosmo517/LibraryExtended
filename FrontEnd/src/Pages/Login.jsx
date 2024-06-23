import React, {useState} from 'react';
import api from '../api';
import Cookies from 'js-cookie';
import '../CSS/login.css';

const GoogleFontsStyle = `
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@700&display=swap');
`;

export const Login = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    })

    const handleFormSubmit = async (event) => {
        event.preventDefault();

        let info = document.getElementById('info')

        let signed_response = await api.post('/login/', formData)
        setFormData({
            username: '',
            password: ''
        })

        if (signed_response['data']['token'])
        {
            // Store the token as a cookie and reroute to the dashboard
            Cookies.set('token', signed_response['data']['token'])
            window.location.href='/';
        }
        else 
        {
            info.innerHTML = 'Invalid username or password'
        }
    };

    const handleInputChange = (event) => {
        const value = event.target.value
        setFormData({
            ...formData,
            [event.target.name]: value,
        });
    };
    return (

        <div className='wrap'>
            <div className={'login-form-box space-mono-bold'}>
                <h3>
                    Login
                </h3>
                <form onSubmit= {handleFormSubmit}>
                    <div className="input-box">
                        <span className="icon"><ion-icon name="person"></ion-icon> </span>
                        <input 
                            type='text'
                            name='username'
                            id='username'
                            required
                            onChange={handleInputChange}
                            value={formData.username}
                        />
                        <label>Username</label>
                    </div>
                    <div className='input-box'>
                        <span className="icon"><ion-icon name="lock-closed"></ion-icon></span>
                        <input 
                            type='password'
                            id='password'
                            name='password'
                            required
                            onChange={handleInputChange}
                            value={formData.password}
                            
                        />
                        <label>Password</label>
                    </div>
                    <button type = 'submit' className='bttn space-mono-bold'>Login</button>
                    <div className='account-register'>
                        <a href="/#register">Register an account</a>
                    </div>
                    <div id="info"></div>
                </form>
            </div>
        </div>
        
    );



};

export default Login;