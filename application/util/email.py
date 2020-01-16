# -*- coding: utf-8 -*-
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.header import Header

import configs


class EmailToolkit(object):
    smtp_host = configs.SMTP_HOST
    smtp_port = configs.SMTP_PORT
    sending_address = configs.SENDING_ADDRESS
    smtp_password = configs.SMTP_PASSWORD
    reply_to = configs.REPLY_TO

    def send_activation_email(self, send_to, username, activate_url):
        email_html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>『Celery Soft 学术』激活账号</title>
        </head>
        <body>
            <div style="font-size: 14px;">
                <p>亲爱的{}：</p>
                <p>您好，感谢注册『Celery Soft 学术』，只差最后一步，就能完成注册，在48小时内点击下面的链接即可：</p>
                <p></p>
                <div><a href="{}">{}</a></div>
                <div>（如果链接无法点击，请将它拷贝到浏览器的地址栏中直接打开）</div>
                <p>如果您最近没有进行注册，或者说您确信您错误地收到了这封邮件，还请忽视这封邮件，我们十分抱歉</p>
                <p>此致，</p>
                <p>Celery Soft 学术</p>
            </div>
            <div style="font-size: 13px; margin-top: 48px;">
                <div>
                    顺便，我们觉得有必要让您知道，如果您自己没有在『Celery Soft 学术』进行注册的话，您收到这封邮件是因为有人在我们网站试图使用您的电子邮箱地址进行用户注册，如若没有您的同意，他是无法完成注册的，请您放心。
                </div>
                <div>
                    如果您想在『Celery Soft 学术』创建一个账号，请前往：
                </div>
                <div>
                    <a href="http://www.celerysoft.science/register/">http://www.celerysoft.science/register/</a>
                </div>
                <div>
                    如果还有任何疑问，可以完成注册之后再登录网站联系客服，谢谢。
                </div>
            </div>
        </body>
        </html>
        '''
        email_html = email_html.format(username, activate_url, activate_url)

        title = '欢迎注册Celery Soft学术'

        self.__send_email(send_to, title, email_html)
        print('用户{}的验证电子邮箱地址的邮件已成功发送至{}'.format(username, send_to))

    def send_activation_email_for_modifying_email_address(self, send_to, username, activate_url):
        email_html = '''
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>『Celery Soft 学术』更换电子邮箱地址</title>
            </head>
            <body>
                <div style="font-size: 14px;">
                    <p>亲爱的{}：</p>
                    <p>您好，您申请更换在『Celery Soft 学术』的电子邮箱地址，只差最后一步，就能完成更换，在48小时内点击下面的链接即可：</p>
                    <p></p>
                    <div><a href="{}">{}</a></div>
                    <div>（如果链接无法点击，请将它拷贝到浏览器的地址栏中直接打开）</div>
                    <p>如果您不是『Celery Soft 学术』的会员，或者说您确信您错误地收到了这封邮件，还请忽视这封邮件，我们十分抱歉</p>
                    <p>此致，</p>
                    <p>Celery Soft 学术</p>
                </div>
                <div style="font-size: 13px; margin-top: 48px;">
                    <div>
                        顺便，我们觉得有必要让您知道，如果您自己没有在『Celery Soft 学术』进行过注册的话，您收到这封邮件是因为有人在我们网站试图将联系方式更改为您的电子邮箱地址，如若没有您的同意，他无法完成这个操作，请您放心。
                    </div>
                    <div>
                        如果您想在『Celery Soft 学术』创建一个账号，请前往：
                    </div>
                    <div>
                        <a href="http://www.celerysoft.science/register/">http://www.celerysoft.science/register/</a>
                    </div>
                    <div>
                        如果还有任何疑问，可以完成注册之后再登录网站联系客服，谢谢。
                    </div>
                </div>
            </body>
        </html>
        '''
        email_html = email_html.format(username, activate_url, activate_url)

        title = '修改在Celery Soft学术的电子邮箱地址'

        self.__send_email(send_to, title, email_html)
        print('用户{}修改电子邮箱地址的验证邮件已成功发送至{}'.format(username, send_to))

    def send_reset_password_email(self, send_to, username, reset_password_url):
        email_html = '''
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>『Celery Soft 学术』重设密码</title>
            </head>
            <body>
                <div style="font-size: 14px;">
                    <p>亲爱的{}：</p>
                    <p>您好，您申请重设在『Celery Soft 学术』的登录密码，只差最后一步，就能完成重设。在1小时内点击下面的链接即可：</p>
                    <p></p>
                    <div><a href="{}">{}</a></div>
                    <div>（如果链接无法点击，请将它拷贝到浏览器的地址栏中直接打开）</div>
                    <p>如果您没有在『Celery Soft 学术』申请重设登录密码，那我们严重怀疑您在『Celery Soft 学术』的密码已经泄漏，请您立即登录网站修改密码。</p>
                    <p>此致，</p>
                    <p>Celery Soft 学术</p>
                </div>
            </body>
        </html>
        '''
        email_html = email_html.format(username, reset_password_url, reset_password_url)

        title = '重设在Celery Soft学术的登录密码'

        self.__send_email(send_to, title, email_html)
        print('用户{}的重设密码邮件已成功发送至{}'.format(username, send_to))

    def __send_email(self, send_to, title, text):
        # 构建alternative结构
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(title, charset='utf-8').encode()
        msg['From'] = '%s <%s>' % (Header('Celery Soft学术', charset='utf-8').encode(), self.sending_address)
        msg['To'] = send_to
        msg['Reply-to'] = self.reply_to
        msg['Message-id'] = email.utils.make_msgid()
        msg['Date'] = email.utils.formatdate()

        if text is not None:
            text_to_attach = MIMEText(text, _subtype='html', _charset='UTF-8')
            msg.attach(text_to_attach)
        else:
            # 构建alternative的text/plain部分
            textplain = MIMEText('自定义TEXT纯文本部分', _subtype='plain', _charset='UTF-8')
            msg.attach(textplain)
            # 构建alternative的text/html部分
            texthtml = MIMEText('自定义HTML超文本部分', _subtype='html', _charset='UTF-8')
            msg.attach(texthtml)

        # 发送邮件
        try:
            client = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            client.login(self.sending_address, self.smtp_password)
            client.sendmail(self.sending_address, send_to, msg.as_string())
            client.quit()

        except smtplib.SMTPConnectError as e:
            print('邮件发送失败，连接失败:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPAuthenticationError as e:
            print('邮件发送失败，认证错误:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPSenderRefused as e:
            print('邮件发送失败，发件人被拒绝:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPRecipientsRefused as e:
            print('邮件发送失败，收件人被拒绝:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPDataError as e:
            print('邮件发送失败，数据接收拒绝:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPException as e:
            print('邮件发送失败, ', e.message)
        except Exception as e:
            print('邮件发送异常, ', str(e))


toolkit = EmailToolkit()
