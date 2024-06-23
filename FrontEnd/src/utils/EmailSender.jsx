import nodemailer from 'nodemailer';
import ConfigParser from 'configparser';
const fs = require('fs')

const config = new ConfigParser();

const devPath = '../../../config/dev.cfg';
const settingsPath = '../../../config/settings.cfg';
let hostEmail = null;
let hostPassword = null;

try {
    if (fs.existsSync(devPath)) {
        config.read(devPath);
        hostEmail = config.get('EMAIL', 'email')
        hostPassword = config.get('EMAIL', 'password')
    }
    else if (fs.existsSync(settingsPath)) {
        config.read(settingsPath);
        hostEmail = config.get('EMAIL', 'email')
        hostPassword = config.get('EMAIL', 'password')
    }
    else {
        console.error("Cannot access any settings or config files in config folder");
    }
} catch (err) {
    console.error(err);
}

const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: hostEmail,
        pass: hostPassword
    }
});

let mailOptions = {
    signup: {
        from: hostEmail,
        to: 'otherperson@email.com',
        subject: 'signup email',
        text: 'signup email from library extended'
    },
    notification: {
        from: hostEmail,
        to: 'otherperson@email.com',
        subject: 'some notification email',
        text: 'a notification email from library extended'
    }
};

function sendEmail(mailType, recipent) {
    email_to_send = mailOptions[mailType];
    email_to_send['to'] = recipent;
    
    transporter.sendMail(email_to_send, function(error, info) {
        if (error) {
            console.log(error);
        }
        else {
            console.log('Email sent: ' + info.response);
        }
    });
}
