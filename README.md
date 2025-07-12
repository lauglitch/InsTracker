# InsTracker

**InsTracker** is a desktop application that analyzes your Instagram data and generates a list of users you follow but who don't follow you back.

> ✅ **New Feature**: You can now exclude accounts from the result using a `followignore.txt` file!

---

## 🌐 Website
[lauglitch.com](https://www.lauglitch.com)

## 📦 Current Version
**1.3.1**

---

## 📥 Prerequisites – Export Your Instagram Data

To use InsTracker, you must first download your Instagram data by following these steps:

1. Go to [Instagram Data Permissions](https://accountscenter.instagram.com/info_and_permissions/)
2. Click:
   - "Download your information"
   - "Download or transfer information"
3. Choose your account
4. Click "Some of your information" and check the option: `Followers and following`
5. Select:
   - **Date range**: `From the beginning`
   - **Format**: `JSON`
   - **Media quality**: `Low`
6. Click "Create files"
7. Wait for the `.zip` file via email (can take up to 48 hours)

---

## 🚀 How to Use

1. [Download the latest version](https://lauglitch.itch.io/instracker)
2. Extract and run `InsTracker.exe`
3. Click **Exportar Datos** and select the Instagram `.zip` file you received
4. The file `exportedData.txt` will be created in the app's root directory
5. (Optional) Add usernames to `followignore.txt` to skip them in results (one per line)

---

## 🛠️ Built With

- [Tkinter](https://wiki.python.org/moin/TkInter) – GUI framework
- [Pygame](https://www.pygame.org/news) – For audio playback

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0**.

---

## 🤝 Contributing

If you'd like to contribute, feel free to fork the repository and submit a pull request.


