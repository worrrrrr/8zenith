import type { PageLoad } from './$types';

export const load: PageLoad = ({ params }) => {
    // ดึงค่า id ออกมาจากพารามิเตอร์ URL และส่งต่อผ่านตัวแปร data
    return {
        chatId: params.id
    };
};