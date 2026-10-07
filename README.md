# Computational Design and Fabrication 1 (CDF1)

## Welcome

Welcome to **Computational Design and Fabrication**, a platform dedicated to beginner-friendly creative coding tutorials and exercises for computational design and fabrication in architecture.


<!-- ## Session Blocks 

Title | Description | Slides | Session material | Assignment 
----- | ----------- | ------ | ---------------- | ---------- -->
<!-- **01a Python Basics** | Quick start on Python | [Python Basics](https://github.com/computationaldesignandfabrication/cdf1_teaching/blob/main/sessions-slides/Session%2001%20Python%20Basics.pdf) | [Session 01a](https://classroom.github.com/a/0gVDlBH0) |[Assignment 01a](https://classroom.github.com/a/gEZq-xda)
**01b Rhino Basics** | Quick start on Rhino | [Rhino Basics](https://github.com/computationaldesignandfabrication/cdf1_teaching/blob/main/sessions-slides/Session%2001%20Rhino%20Basics.pdf) |  |
**02 Geometry 2D** | 2D geometry  | [Geometry 2D](https://github.com/computationaldesignandfabrication/cdf1_teaching/blob/main/sessions-slides/Session%2002%20Geometry%202D.pdf) | [Session 02](https://classroom.github.com/a/tBISN_ul) | [Assignment 02](https://classroom.github.com/a/FkT2TYiD)
**03 Basic Geometry 3D** | 3D primitive geometry  | [Geometry 3D](https://github.com/computationaldesignandfabrication/cdf1_teaching/blob/main/sessions-slides/Session%2003%20Basic%20Geometry%203D.pdf) | [Session 03](https://classroom.github.com/a/331M5qJj) | [Assignment 03](https://classroom.github.com/a/piywCTG7)
**04 Meshses** | Meshes and mesh operations | [Meshes](https://github.com/computationaldesignandfabrication/cdf1_teaching/blob/main/sessions-slides/Session%2004%20Meshes.pdf) |  [Session 04](https://classroom.github.com/assignment-invitations/380e9596c1d28ade12d9917156004a25/status) | [Assignment 04](https://classroom.github.com/assignment-invitations/6641726eccea3b9db9017547b04649f2/status)
**05 Integrated Representations** | Integrated design and fabrication representations | [Integrated Representation](https://github.com/computationaldesignandfabrication/cdf1_teaching/blob/main/sessions-slides/Session%2005%20Integrated%20Representations.pdf) | [Session 05](https://classroom.github.com/a/J5fiLqqq) |
**06 Design Algorithms** | Generative methods for creating form and structure | [Design Algorithms](https://github.com/computationaldesignandfabrication/cdf1_teaching/blob/main/sessions-slides/Session%2006%20Design%20Algorithms.pdf) | [Session 06](https://classroom.github.com/a/5SiJajj8) |
**07 Structural Form Finding** | Geometric form finding for compression-only structures | [Structural Form Finding]() | [Session 07]() | -->


## Requirements

* Rhino 8 / Grasshopper
* [Github Desktop](https://desktop.github.com/)
* [Visual Studio Code](https://code.visualstudio.com/)

## Installation

### Cloning the CDF Repository to your workstation

1. Create a **workspace** folder in File Explorer:

    `C:\Users\your_username\workspace`

2. Open **GitHub Desktop** and click **Current Repository** (top left), then **Add > Clone Repository...**.

3. Select the **URL** tab and paste:

    `https://github.com/computationaldesignandfabrication/cdf1_teaching.git`

4. Set the **Local Path** (bottom) so it looks like:

    `C:\Users\your_username\workspace\cdf1_teaching`

5. Click **Clone**.

### Setting up your GitHub Copilot account

1. Create a free [GitHub account](https://github.com/signup) if you do not have one yet.

2. As a TUM student, you are eligible for free **GitHub Pro** and **GitHub Copilot Pro**. Request them by following the [TUM GitHub guide](https://collab.dvb.bayern/spaces/TUMsoftware/pages/2662964764/GitHub) (TUM login required).

### Setting up VS Code and extensions

1. Install the extensions. Open the Extensions panel (`Ctrl+Shift+X`), search for each one and click **Install**:
    * **Python** (by Microsoft): syntax highlighting and code help for Python files.
    * **GitHub Copilot** (by GitHub): the AI assistant. This also installs **GitHub Copilot Chat**.

2. Log in to your Copilot account:
    * Click the Copilot icon in the VS Code status bar (bottom right) or the account icon (bottom left) and choose **Sign in with GitHub**.
    * Sign in with your GitHub account in the browser and authorize VS Code.

3. Check that it works: open the Copilot Chat panel (`Ctrl+Alt+I`) and send a short message. If you get an answer, you are ready.

### Setting up Rhino/Grasshopper

This tells Rhino's Python where to find the CDF code, so you can `import` it in Grasshopper.

1. Open **Rhino 8** and start **Grasshopper** (type `Grasshopper` in the Rhino command line).

2. Add a **Python 3 Script** component to the canvas. The first time, wait for it to finish loading.

3. Double-click the component to open the script editor.

4. In the editor's top bar, go to **Tools > Options**.

5. Open the **Python 3** tab.

6. Under **Module search paths**, click **+** and add the path to the `src` folder of your cloned repository:

    `C:\Users\your_username\workspace\cdf1_teaching\src`

7. Click **Save**.

8. Check that it works: in the component, run `import cdf` (or one of the CDF modules). If there is no error, the path is set up correctly.


**Done! Now you can go to VS Code, Rhino, or Grasshopper to run the example files of CDF.**
