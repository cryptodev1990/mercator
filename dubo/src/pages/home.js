import Header from 'dubo/components/header';
import PostCard from 'dubo/components/postcard';

const posts = [
  {
    title: 'Tracking inflation outside of the CPI',
    author: 'Andrew Duberstein',
    tag: 'New',
    byline: 'This is a byline, which should probably span about two lines but no more',
    publishedAt: '2022 May 21'
  },
  {
    title: 'What will America do with all its vacant commercial real estate?',
    author: 'Dayton Thorpe',
    tag: 'New',
    byline: 'This is a byline, which should probably span about two lines but no more',
    publishedAt: '2022 May 21'
  },
  {
    title: 'Tracking the NFT market collapse',
    author: 'Richard Gong',
    tag: 'New',
    byline: 'This is a byline, which should probably span about two lines but no more',
    publishedAt: '2022 May 21'
  },
  {
    title: 'What industries are being affected by layoffs?',
    author: 'Andrew Duberstein',
    tag: 'Economics',
    byline:
      'Based on public data, can we figure out what industries are safe and what jobs are at risk?',
    publishedAt: '2022 June 14'
  },
  {
    title: 'The growth and decline of San Francisco',
    author: 'Andrew Duberstein',
    tag: 'New',
    byline: 'Visualizing the history of San Francisco using data from archival phone books',
    publishedAt: '2022 May 21'
  }
];

function HomePage() {
  return (
    <>
      <Header />
      <section class="bg-white">
        <div class="w-full px-5 py-6 mx-auto space-y-5 sm:py-8 md:py-12 sm:space-y-8 md:space-y-16 max-w-7xl">
          <div class="flex flex-col items-center sm:px-5 md:flex-row">
            <PostCard
              post={{
                title: 'How can we track economic recovery?',
                tag: 'Featured',
                author: 'Andrew Duberstein',
                publishedAt: 'May 22, 2022'
              }}
            />
          </div>
          <div class="flex grid grid-cols-12 pb-10 sm:px-5 gap-x-8 gap-y-16">
            {posts.map((post) => {
              return <PostCard small post={post} />;
            })}
          </div>
        </div>
      </section>
    </>
  );
}

export { HomePage };
