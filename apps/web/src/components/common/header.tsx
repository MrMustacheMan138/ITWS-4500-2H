
import Image from "next/image";
import logo from "@/assets/syllabusai.png";
import LoginButton from "./auth/login";

export default function Header() {
   return (
      <header className="bg-gray-800 text-white w-full flex items-center justify-start">
         <div className="flex items-center gap-1">
            <Image src={logo} alt="Project Logo" width={100} height={100} />
            <div>
               <div className="text-sm text-[#3B82F6]">SyllabusAI</div>
               <div className="text-xl font-bold">AI Curriculum Benchmarking</div>
            </div>
         </div>
         <div className="ml-auto mr-8">
            <LoginButton />
         </div>
      </header>
   );
}