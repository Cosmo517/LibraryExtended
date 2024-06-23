import React from 'react';
import '../CSS/navbar.css';

export const Navbar =() => {
    return(
        <header>
            <h2 className = 'navbar-logo'>Library XT</h2>
            <nav className='navbar-set'>
                <div className="navbar-search">
                    <input type = "text" placeholder="Search books"/>
                    <button className = "search-bttn">Search</button>
                    <a href = "/#Dashboard">Home</a>
                    <a href = "/#mylists">My List</a>
                    <u1 className="drop-down">
                        <li href = "/#Profile"> Settings</li>
                        <li href = "/#Settings"> Settings</li>
                        <li href = "/#Login"> Settings</li>
                        <li href = "/#Register"> Settings</li>
                    </u1>
                </div>

            </nav>
        </header>
    )



}