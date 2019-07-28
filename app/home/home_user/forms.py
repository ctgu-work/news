# coding:utf8

from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, ValidationError
from wtforms import validators, widgets


class UserBaseForm(FlaskForm):
    """用户基本信息表单 """
    # 个性签名
    signature = StringField(
        label="个性签名",
        validators=[  # 验证器
            validators.DataRequired(message="用户名不能为空"),
            validators.Length(max=20, min=3, message="个性签名长度必须小于%(max)d且大于%(min)d")

        ],
        description="个性签名",
        render_kw={
            "class": "input_txt",
            "required": "required",
            "placeholder": "请输入个性签名"
        }
    )

    # 昵称
    nick_name = StringField(
        label="昵称",
        validators=[
            validators.DataRequired('请输入昵称！'),
            validators.Length(max=10, min=1, message="昵称长度必须小于%(max)d且大于%(min)d")
        ],
        description="昵称",
        render_kw={
            "class": "input_txt",
            "required": "required",
            "placeholder": "请输入昵称"
        }
    )

    # 性别
    gender = RadioField(
        label="性别",
        description="性别",
        validators=[
            DataRequired()
        ],
        coerce=str,
        choices=[
            ("MAN", '男'),  # Male
            ("WOMAN", '女')  # FeMale
        ],
        default="MAN",
        render_kw={
            "style": "display:inline-flex",
        }

    )
    submit = SubmitField(
        '确认',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }

    )


"""修改密码"""


class ModifyPassowrd(FlaskForm):
    oldPassword = PasswordField(
        label="当前密码",
        validators=[  # 验证器
            validators.DataRequired(message="密码不能为空"),
            # validators.Length(max=20, min=3, message="密码长度必须小于%(max)d且大于%(min)d")
        ],
        render_kw={
            "class": "input_txt"
        }
    )
    newPassword = PasswordField(
        label="新密码",
        validators=[  # 验证器
            validators.DataRequired(message="密码不能为空"),
            validators.Length(max=16, min=8, message="密码长度必须小于%(max)d且大于%(min)d")
        ],
        render_kw={
            "class": "input_txt"
        }
    )
    confirmPassword = PasswordField(
        label="重复密码",
        validators=[  # 验证器
            validators.DataRequired(message="密码不能为空"),
            validators.EqualTo('newPassword', message='两次密码不一致')
        ],
        render_kw={
            "class": "input_txt"
        }
    )

    submit = SubmitField(
        '提交',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )


class UserImg(FlaskForm):
    url = FileField(
        label="上传头像: ",
        validators=[
            DataRequired("请上传图片")
        ],
        description="头像"
    )
    
    submit = SubmitField(
        '提交',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }

    )
