# FastAPI App with VueJS dist 

## Dependencies
### backend
- `fastapi==0.70.0`
- `pydantic==1.8.2`
- `python-dotenv==0.19.1`


### frontend
- `npm@8.19.4`
- `node@16.20.2`
- `yarn@1.22.21`
- `vue@3.4.27`
- `dotenv@16.4.5`


## Frontend
### Create Frontend project

1. Install npm, node
2. create a vue project (project name: simpleproj) with `vite` (default)

    ```shell
    $ npm create vue 
    ✔ Project name: … simpleproj
    ✔ Add TypeScript? … No / Yes
    ✔ Add JSX Support? … No / Yes
    ✔ Add Vue Router for Single Page Application development? … No / Yes
    ✔ Add Pinia for state management? … No / Yes
    ✔ Add Vitest for Unit testing? … No / Yes
    ✔ Add an End-to-End Testing Solution? … No / Cypress / Nightwatch / Playwright
    ✔ Add ESLint for code quality? … No / Yes
    ✔ Add Prettier for code formatting? … No / Yes
    ✔ Add Vue DevTools 7 extension for debugging? (experimental) … No / Yes

    cd simpleproj
    ```

3. Install required packages

    ```shell
    $ npm install dotenv
    ```

4. create `.env` and `.env.production` files

    - The `.env` file is for development

        ```
        # .env
        VITE_API_URL="/simple"
        VITE_PRODUCT_NAME="AAA"
        ```

    - The `.env.production` file will be use as build environment, and the setting is to fit jinja template syntax which is required by backend `FastAPI` service

        ```
        # .env.production
        VITE_API_URL="{{ url_for('root') }}"
        VITE_PRODUCT_NAME="{{ PRODUCT_NAME }}"
        ```

5. Use varaibles from `dotenv`: Add lines in `src/App.vue` for testing

    ```html 
    ...
    <template>
      <header>
        <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />

        <div class="wrapper">
          <HelloWorld msg="You did it!" />
          <div>{{ API_URL }}</div>
          <div>{{ PRODUCT_NAME }}</div>
        </div>
      </header>

      <main>
        <TheWelcome />
      </main>
    </template>

    <script>
    const API_URL = import.meta.env.VITE_API_URL
    const PRODUCT_NAME = import.meta.env.VITE_PRODUCT_NAME
    console.log(API_URL)
    console.log(PRODUCT_NAME)
    </script>
    ...
    ```

6. Setup build configuration for backend service (`FastAPI`) templaing

    - In `package.json`: to assign output folder

        ```json
        {
          ...
          "scripts": {
            ...
            "build": "vite build --emptyOutDir",
            ...
          },
          ...
        }
        ```

    - In `vite.config.js`: to separate output files by extension (js,html, and others)

        ```js
        ...

        export default defineConfig({
            ...
          build: {
            outDir:  '../frontend',
            rollupOptions: {
              output: {
                assetFileNames: 'asset/[name]-[hash][extname]',
                chunkFileNames: 'scripts/[name]-[hash].js',
                entryFileNames: 'scripts/[name]-[hash].js',
              },
            },
          },
        })
        ```


### Install packages and Run dev

1. Install packages
    ```shell
    $ cd simpleproj
    $ npm install
    ```

2. Run dev

    ```shell
    $ npm run dev
    ```

    or with expose options

    ```shell
    $ npm run dev -- --host 0.0.0.0 --port 3000
    ```

### Build

```shell
$ npm run build
```

## Backend

### Install dependencies

```shell 
$ pip install -e requirements.txt
```

### Run 

1. Make sure there are frontend build files in `./frontend`

```
▾ frontend/
  ▾ asset/
      index-af4ea314.css
      logo-da9b9095.svg
  ▾ scripts/
      index-49d00d81.js
    favicon.ico
    index.html
```

2. Run app

    By default

    ```shell 
    $ uvicorn main:app
    ```

    or with options

    ```shell 
    $ uvicorn main:app --host=0.0.0.0 --port=8000 --debug
    ```
