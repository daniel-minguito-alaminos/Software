# BizPartnerCheck frontend

Vue and Vite frontend with a construction blueprint homepage and matching login and registration forms.

Use the Node.js version specified in package.json. From this folder in Windows PowerShell:

    npm.cmd ci
    npm.cmd run dev

Open the Local URL shown in the terminal. Run npm.cmd run build to produce dist/.
Configure the host to serve index.html for client-side routes such as /login and /register.

The forms are UI previews. They validate required inputs and send no requests.
Registration collects details for email verification before password setup.
