import Tag from '../tag';

const PostCard = ({ post, small }) => {
  const { title, author, tag, publishedAt, image, byline } = post;
  if (small) {
    return (
      <div class="flex flex-col items-start col-span-12 space-y-3 sm:col-span-6 xl:col-span-4">
        <a href="#_" class="block">
          <img
            class="object-cover w-full mb-2 overflow-hidden rounded-lg shadow-sm max-h-56"
            src={image}></img>
        </a>
        <Tag>{tag}</Tag>
        <h2 class="text-lg font-bold sm:text-xl md:text-2xl">{title}</h2>
        <p class="text-sm text-gray-500">{byline}</p>
        <p class="pt-2 text-xs font-medium">
          <a href="#_" class="mr-1 underline">
            {author}
          </a>{' '}
          · <span class="mx-1">{publishedAt}</span> ·{' '}
          <span class="mx-1 text-gray-600">3 min. read</span>
        </p>
      </div>
    );
  }
  return (
    <>
      <div class="w-full md:w-1/2">
        <a href="#_" class="block">
          <img class="object-cover w-full h-full rounded-lg max-h-64 sm:max-h-96" src={image}></img>
        </a>
      </div>

      <div class="flex flex-col items-start justify-center w-full h-full py-6 mb-6 md:mb-0 md:w-1/2">
        <div class="flex flex-col items-start justify-center h-full space-y-3 transform md:pl-10 lg:pl-16 md:space-y-5">
          <Tag>ktag}</Tag>
          <h1 class="text-4xl font-bold leading-none lg:text-5xl xl:text-6xl">
            <a href="#_">{title}</a>
          </h1>
          <p class="pt-2 text-sm font-medium">
            by{' '}
            <a href="#_" class="mr-1 underline">
              {author}
            </a>{' '}
            · <span class="mx-1">{publishedAt}</span> ·{' '}
            <span class="mx-1 text-gray-600">{'5 min read'}</span>
          </p>
        </div>
      </div>
    </>
  );
};

export default PostCard;
