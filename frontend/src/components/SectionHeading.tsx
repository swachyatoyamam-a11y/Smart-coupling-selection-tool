import { motion } from 'framer-motion';
import type { ReactNode } from 'react';
export function SectionHeading({eyebrow,title,children}:{eyebrow:string;title:string;children?:ReactNode}) { return <motion.div initial={{opacity:0,y:14}} whileInView={{opacity:1,y:0}} viewport={{once:true}} transition={{duration:.45}}><span className="eyebrow">{eyebrow}</span><h2 className="mt-3 text-3xl font-bold text-ink dark:text-white">{title}</h2>{children}</motion.div>; }
