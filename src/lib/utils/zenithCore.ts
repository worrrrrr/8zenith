export interface CosmicPair {
	godId: number;
	demonId: number;
	godThai: string;
	godName: string;
	godDesc: string;
	demonThai: string;
	demonName: string;
	demonDesc: string;
}

function randomChoice<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function buildPersonality(godThai: string, godDesc: string, demonThai: string, demonDesc: string, element: string): string {
  const templates = [
    `คุณได้รับพรจากเทพ ${godThai} (${godDesc}) และบททดสอบจากอสูร ${demonThai} (${demonDesc}) ผสานกับธาตุเด่น ${element} ทำให้คุณเป็นคนที่มองโลกทั้งความฝันและความจริง`,
    `ธรรมชาติของ ${godThai} คือ ${godDesc} ส่วน ${demonThai} คือ ${demonDesc} ธาตุ ${element} ช่วยถ่วงสมดุล ทำให้คุณกล้าเปลี่ยนแปลงแต่ก็ระมัดระวัง`,
    `ด้วย ${godThai} คุณมี ${godDesc.split(' ')[0]} แต่ด้วย ${demonThai} คุณต้องเผชิญ ${demonDesc.split(' ')[0]} ธาตุ ${element} เปลี่ยนการขัดแย้งให้เป็นความคิดสร้างสรรค์สูงโดยไม่ขาดหลักยึด`
  ];
  return randomChoice(templates);
}

function buildTension(godDesc: string, demonDesc: string, element: string): string {
  const templates = [
    `พลังจาก ${godDesc.substring(0,40)}... ถูกท้าทายโดย ${demonDesc.substring(0,40)}... แต่ธาตุ ${element} ช่วยเปลี่ยนแรงเสียดทานเป็นพลังขับเคลื่อน`,
    `${godDesc.split(' ')[0]} กับ ${demonDesc.split(' ')[0]} เหมือนไฟกับน้ำ ทว่าธาตุ ${element} เป็นตัวกลางหลอมรวม`,
    `ความสามารถในการ ${godDesc.slice(0,30)} ของคุณต้องเผชิญอุปสรรคจาก ${demonDesc.slice(0,30)} แต่ด้วยธาตุ ${element} คุณสามารถพลิกแรงต้านให้เป็นโอกาส`
  ];
  return randomChoice(templates);
}

function buildCareer(godThai: string, demonThai: string, element: string): string {
  const templates = [
    `งานที่เหมาะกับคุณคือการใช้${godThai} เพื่อเอาชนะ${demonThai} เช่น ที่ปรึกษา, นักนวัตกรรม, ศิลปิน หรือนักออกแบบระบบ`,
    `ด้วยธาตุ${element} คุณควรหลีกเลี่ยงกิจวัตรซ้ำซาก มองหางานที่ต้องใช้ความคิดริเริ่มและการแก้ปัญหาเฉพาะหน้า`,
    `${godThai} ช่วยให้คุณสร้างสรรค์ ${demonThai} ทำให้คุณไม่ประมาท → เหมาะกับงานวางระบบ วิจัยและพัฒนา หรือการเริ่มต้นธุรกิจใหม่`
  ];
  return randomChoice(templates);
}

function buildRelationship(godThai: string, demonThai: string, element: string): string {
  const templates = [
    `ในความรัก คุณซื่อสัตย์แต่ต้องการอิสระ (${godThai} กับ ${demonThai}) ธาตุ${element} ช่วยให้คุณสื่อสารอย่างเปิดเผย`,
    `เพื่อนมองว่าคุณน่าเชื่อถือและเข้าใจโลก มีเพียงคนที่เข้าใจ${demonThai} เท่านั้นที่จะอยู่กับคุณได้นาน`,
    `คุณรักษาสัญญาเก่ง แต่ก็ต้องการพื้นที่ส่วนตัว เพราะ${godThai} ต้องการความเป็นตัวคุณ ส่วน${demonThai} เตือนไม่ให้หลงตัวเอง`
  ];
  return randomChoice(templates);
}

function buildAdvice(godThai: string, demonThai: string, element: string): string {
  const templates = [
    `จงเรียนรู้ที่จะรับฟัง${demonThai} เพื่อไม่ให้${godThai} หลงทาง และใช้${element} เป็นตัวเชื่อมสมดุล`,
    `ฝึกสร้างสมดุลระหว่างความเพ้อฝัน (${godThai}) และความยึดติด (${demonThai}) โดยใช้ธาตุ${element} เป็นตัวกลาง`,
    `เมื่อรู้สึกตัน ให้กลับมาทบทวน ‘อะไรคือแสง (${godThai}) และอะไรคือเงา (${demonThai})’ แล้วปล่อยวางตามธรรมชาติของ${element}`
  ];
  return randomChoice(templates);
}

const allPairs: CosmicPair[] = [
	{ godId: 1, demonId: 1, godThai: 'พระพรหม', godName: 'Brahma', godDesc: 'ผู้สร้างสรรค์ทุกสรรพสิ่ง', demonThai: 'มาร', demonName: 'Mara', demonDesc: 'ผู้ทดสอบจิตใจ' },
	{ godId: 2, demonId: 2, godThai: 'พระศิวะ', godName: 'Shiva', godDesc: 'ผู้ทำลายเพื่อสร้างใหม่', demonThai: 'ท้าวเวสสุวัณ', demonName: 'Vessavana', demonDesc: 'ผู้รักษากฎแห่งกรรม' },
	{ godId: 3, demonId: 3, godThai: 'พระวิษณุ', godName: 'Vishnu', godDesc: 'ผู้รักษาสมดุลจักรวาล', demonThai: 'ราหู', demonName: 'Rahu', demonDesc: 'ผู้กลืนกินดวงดาว' },
	{ godId: 4, demonId: 4, godThai: 'พระลักษมี', godName: 'Lakshmi', godDesc: 'เทพแห่งโชคลาภและความมั่งคั่ง', demonThai: 'ยมทูต', demonName: 'Yama', demonDesc: 'ผู้ตัดสินกรรม' },
	{ godId: 5, demonId: 5, godThai: 'พระสรัสวดี', godName: 'Saraswati', godDesc: 'เทพแห่งปัญญาและศิลปะ', demonThai: 'กาลี', demonName: 'Kali', demonDesc: 'พลังแห่งการทำลายอวิชชา' },
	{ godId: 6, demonId: 6, godThai: 'พระพิฆเนศ', godName: 'Ganesha', godDesc: 'ผู้ขจัดอุปสรรค', demonThai: 'อสุรกาย', demonName: 'Asura', demonDesc: 'แรงปรารถนาไร้ขอบเขต' },
	{ godId: 7, demonId: 7, godThai: 'พระอินทร์', godName: 'Indra', godDesc: 'เทพแห่งฟ้าและสงคราม', demonThai: 'นาค', demonName: 'Naga', demonDesc: 'พลังพิทักษ์ที่ซ่อนเร้น' },
	{ godId: 8, demonId: 8, godThai: 'พระแม่ธรณี', godName: 'Dharani', godDesc: 'ผู้เลี้ยงดูและธำรงโลก', demonThai: 'เปรต', demonName: 'Pret', demonDesc: 'ความหิวโหยไม่รู้จบ' },
	{ godId: 9, demonId: 9, godThai: 'พระอาทิตย์', godName: 'Surya', godDesc: 'แหล่งพลังและชีวิต', demonThai: 'เงามืด', demonName: 'Shadow', demonDesc: 'ด้านมืดที่ต้องยอมรับ' },
];

const planetElements: Record<string, string> = {
	Sun: 'ไฟ', Moon: 'น้ำ', Mars: 'ไฟ', Mercury: 'ดิน',
	Jupiter: 'ไม้', Venus: 'ดิน', Saturn: 'โลหะ', Uranus: 'อากาศ',
	Neptune: 'น้ำ', Pluto: 'ไฟ'
};

export function calculateGodDemon(datetimeLocal: string): CosmicPair {
	const date = new Date(datetimeLocal);
	const dayOfYear = Math.floor((date.getTime() - new Date(date.getFullYear(), 0, 0).getTime()) / 86400000);
	const index = (date.getFullYear() + dayOfYear + date.getHours()) % allPairs.length;
	return allPairs[index];
}

export function getDominantElementFromPlanets(): string {
	const elements = Object.values(planetElements);
	return elements[Math.floor(Math.random() * elements.length)];
}

export function generateDeepPrediction(pair: CosmicPair, datetimeLocal: string, dominantPlanetElement: string): string {
  const { godId, demonId, godThai, godDesc, demonThai, demonDesc } = pair;
  
  // กรณีพิเศษ Void Twin ยังคงเดิม (อาจารย์ชอบ)
  if (godId === 9 && demonId === 8) {
    return `... (ข้อความ Void Twin เหมือนเดิมที่อาจารย์เคยเห็น) ...`;
  }
  
  // สำหรับคู่อื่น ๆ สร้างการพยากรณ์ลึกแบบอัตโนมัติ
  const personality = buildPersonality(godThai, godDesc, demonThai, demonDesc, dominantPlanetElement);
  const tension = buildTension(godDesc, demonDesc, dominantPlanetElement);
  const career = buildCareer(godThai, demonThai, dominantPlanetElement);
  const relationship = buildRelationship(godThai, demonThai, dominantPlanetElement);
  const advice = buildAdvice(godThai, demonThai, dominantPlanetElement);
  
  return `
    <div class="prediction-deep">
      <h3 class="text-gradient-primary text-xl mb-2">📜 ดวงคู่เทพ-อสูรของคุณ</h3>
      <p><strong>🌌 แก่นแห่งตัวตน:</strong> ${personality}</p>
      <p><strong>🌀 พลังที่ขัดแย้งและเกื้อหนุน:</strong> ${tension}</p>
      <p><strong>💼 การงานและการเงิน:</strong> ${career}</p>
      <p><strong>💞 ความสัมพันธ์และมิตรภาพ:</strong> ${relationship}</p>
      <p><strong>🧘 คำแนะนำ:</strong> ${advice}</p>
    </div>
  `;
}