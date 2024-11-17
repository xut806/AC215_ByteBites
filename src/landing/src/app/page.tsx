import { Container } from "@/components/Container";
import { Hero } from "@/components/Hero";
import { SectionTitle } from "@/components/SectionTitle";
import { Benefits } from "@/components/Benefits";
import { Testimonials } from "@/components/Testimonials";
import { Faq } from "@/components/Faq";
import { Cta } from "@/components/Cta";
import Steps from "@/components/Steps";

import { benefitOne } from "@/components/data";

export default function Home() {
  return (
    <Container>
      <Hero />
      <SectionTitle
        preTitle="Features"
        title="Everything you need for your meals"
      >
        Your ultimate solution for automated process to create smarter, healthier, 
        and more sustainable meal planning. 
      </SectionTitle>

      <Benefits data={benefitOne} id="features"/>

      <SectionTitle
        preTitle="Here's how ByteBites works"
        title={
          <>
            Create your meals in <span className="text-pink-500">3 simple steps</span>. Automated
          </>
        }
      >
        Upload your grocery receipt, 
        set your preferences, 
        and ByteBites will <strong>generate the best recipes for you</strong>. 
        Let us handle the details while you <strong>focus on cooking and enjoying delicious meals</strong>.
      </SectionTitle>

      <div id="features">
        <Steps />
      </div>

      <SectionTitle
        preTitle="What Users Are Saying"
        title="Here's how ByteBites changed their meal prep"
      >
        Real stories from ByteBites users who simplified their cooking, reduced waste, and embraced healthier eating.
      </SectionTitle>

      <Testimonials />

      {/* <SectionTitle preTitle="FAQ" title="Frequently Asked Questions">
        Answer your customers possible questions here, it will increase the
        conversion rate as well as support or chat requests.
      </SectionTitle>

      <Faq /> */}
      <Cta />
    </Container>
  );
}
