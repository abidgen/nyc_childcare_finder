mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"abidgen69@gmail.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\


echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml


echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/secrets.toml
