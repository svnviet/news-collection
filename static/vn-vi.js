function getContentNewsFeed(item) {
    const a = document.createElement('a');
    a.href = `/vn-vi/news/${item.link}`;
    a.target = '_blank';

    if (item.image_url && !item.is_long) {
        a.className = 'block col-span-1 row-span-1';
        a.innerHTML = `
        <div class="bg-white rounded-xl shadow overflow-hidden h-full flex">
            <div class="w-3/5 p-2 flex flex-col">
                <div>
                    <img src="/static/${item.source_logo_url}" alt="Source Logo" class="h-4 mb-1">
                </div>
                <h4 class="text-sm font-semibold line-clamp-3">${item.title}</h4>
            </div>
            <div class="w-2/5 p-2 flex items-center justify-center">
                <img src="${item.image_url}" alt="" class="w-full h-full object-cover border border-gray-300 rounded-md">
            </div>
        </div>
    `;
    } else if (item.image_url && item.is_long) {
        a.className = 'block col-span-1 sm:col-span-2 lg:col-span-2 row-span-3';
        a.innerHTML = `
        <div class="bg-white rounded-xl shadow overflow-hidden h-full flex">
            <div class="w-2/5 p-2 flex flex-col">
                <div>
                    <img src="/static/${item.source_logo_url}" alt="Source Logo" class="h-4 mb-1">
                </div>
                <div class="pt-3">
                    <h4 class="text-sm font-semibold line-clamp-3">${item.title}</h4>
                </div>
                <div class="pt-3">
                    <h4 class="text-sx line-clamp-7">${stripTags(item.description || '')}</h4>
                </div>
            </div>
            <div class="w-3/5 p-2 flex items-center justify-center">
                <img src="${item.image_url}" alt="" class="w-full h-full object-cover border border-gray-300 rounded-md">
            </div>
        </div>
    `;
    } else {
        a.className = 'block';
        a.innerHTML = `
        <div class="bg-white rounded-xl shadow overflow-hidden h-[100px] p-2 flex flex-col">
            <div class="flex w-full">
                <div class="w-3/5 flex items-center">
                    <img src="/static/${item.source_logo_url}" alt="Source Logo" class="h-4">
                </div>
                <div class="w-2/5 flex items-center justify-start">
                    <h4 class="text-xs text-gray-600 line-clamp-1">Chuyên mục</h4>
                </div>
            </div>
            <div class="pt-5">
                <h4 class="text-sm font-semibold line-clamp-2">${item.title}</h4>
            </div>
        </div>
    `;
    }

    return a;
}

function stripTags(html) {
    const tmp = document.createElement('DIV');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

function newsFeed() {
    return {
        page: 2,
        loading: false,
        end: false,
        async init() {
            // already loaded page 1 via server-side rendering
        },
        async loadMore() {
            if (this.loading || this.end) return;
            this.loading = true;
            try {
                const res = await fetch(`/load_more?page=${this.page}`);
                const data = await res.json();
                if (!data.length) {
                    this.end = true;
                    return;
                }
                const container = document.getElementById("news-container");
                data.forEach(item => {
                    const newsFeedElement = getContentNewsFeed(item);
                    container.appendChild(newsFeedElement);
                });
                this.page++;
            } finally {
                this.loading = false;
            }
        },
        handleScroll() {
            if ((window.innerHeight + window.scrollY) >= (document.body.offsetHeight - 300)) {
                this.loadMore();
            }
        }
    }
}

function newsDetailFeed() {
    return {
        page: 0,
        loading: false,
        end: false,

        async init_detail_feed() {
            await this.addElement();
        },

        async loadMore() {
            if (this.loading || this.end) return;
            this.loading = true;
            try {
                for (let i = 0; i < 2; i++) {
                    await this.addElement();
                }
            } catch (e) {
                console.error("Failed to load combined feed:", e);
            } finally {
                this.loading = false;
            }
        },

        async addElement() {
            const res = await fetch(`/load_related?page=${this.page}`);
            const data = await res.json();

            if (!data.news_html.trim() && !data.consumption_html.trim()) {
                this.end = true;
                return;
            }

            const wrapper = document.createElement("section");
            wrapper.innerHTML = `
                    <section class="max-w-7xl mx-auto p-4">${data.news_html}</section>
                    <section class="container">${data.consumption_html}</section>
                `;
            document.getElementById("news-detail-feed").appendChild(wrapper);
            this.page++;
        },

        handleScroll() {
            if ((window.innerHeight + window.scrollY) >= (document.body.offsetHeight - 300)) {
                this.loadMore();
            }
        }
    }
}


function thoiGianTruoc(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) return `${diffMins} phút trước`;
    if (diffHours < 24) return `${diffHours} giờ trước`;
    return `${diffDays} ngày trước`;
}
