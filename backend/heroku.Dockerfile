FROM python:3.12.3-slim-bullseye AS base

ENV APP_NAME    vendi
ENV PREFIX      /backend
ENV PREFIX_APP  ${PREFIX}/${APP_NAME}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="${PREFIX_APP}:${PYTHONPATH}"

ENV POETRY_VERSION  1.8.3
ENV POETRY_VIRTUALENVS_IN_PROJECT=false

ENV VIRTUAL_ENV="${PREFIX}/venv/"
ENV PATH="${PREFIX}/venv/bin:$PATH"
ENV HOME=${PREFIX}

WORKDIR ${PREFIX_APP}

FROM base AS deps

RUN apt-get update \
    && apt-get install g++ wget curl -y \
    && apt-get install --no-install-recommends -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Install poetry and create virtual environment for local development
RUN python -m pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && python -m venv --copies "${VIRTUAL_ENV}"

COPY ./poetry.lock ./pyproject.toml ./

COPY . ${PREFIX_APP}

# Install production dependencies
RUN poetry install --without dev --no-root

RUN python manage.py collectstatic --noinput --clear
ENV PORT=8080
RUN chmod u+x ${PREFIX_APP}/heroku-entrypoint.sh

CMD ["/backend/vendi/heroku-entrypoint.sh"]