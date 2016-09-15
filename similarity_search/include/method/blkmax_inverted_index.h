/**
 * Non-metric Space Library
 *
 * Authors: Bilegsaikhan Naidan (https://github.com/bileg), Leonid Boytsov (http://boytsov.info).
 * With contributions from Lawrence Cayton (http://lcayton.com/) and others.
 *
 * For the complete list of contributors and further details see:
 * https://github.com/searchivarius/NonMetricSpaceLib 
 * 
 * Copyright (c) 2016
 *
 * This code is released under the
 * Apache License Version 2.0 http://www.apache.org/licenses/.
 *
 */
#ifndef _BLKMAX_INV_INDEX_H_
#define _BLKMAX_INV_INDEX_H_

#include "wand_inverted_index.h"
#include <stdexcept>

#define METH_BLKMAX_INV_INDEX             "blkmax_invindx"

#define PARAM_BLOCK_SIZE                  "blk_size"
#define PARAM_BLOCK_SIZE_DEFAULT          64

namespace similarity {

using std::string;

template <typename dist_t>
class BlockMaxInvIndex : public WandInvIndex<dist_t> {
 public:
  BlockMaxInvIndex(Space<dist_t>& space,
              const ObjectVector& data) : WandInvIndex<dist_t>(space, data) {
  }

  void CreateIndex(const AnyParams& IndexParams) override; 

  void SetQueryTimeParams(const AnyParams& QueryTimeParams) override;

  ~BlockMaxInvIndex() override;

  void Search(KNNQuery<dist_t>* query, IdType) const override;


  const string StrDesc() const override {
    return METH_WAND_INV_INDEX;
  }

 protected:

  typedef typename SimplInvIndex<dist_t>::PostList PostList;
  typedef typename SimplInvIndex<dist_t>::PostEntry PostEntry;
  typedef typename WandInvIndex<dist_t>::PostListQueryStateWAND PostListQueryStateWAND;

  // record with information about a block of entries in the inverted list
  struct BlockInfo {
    // last doc_id in the block
    const IdType last_id;
    // maximum value of all records in the block
    const dist_t max_val;

    BlockInfo(const IdType last_id_param, const dist_t max_val_param)
        : last_id(last_id_param), max_val(max_val_param) {}
  };

  /**
   * A structure that keeps information about current state of search within one posting list (for WAND).
   */
  struct PostListQueryStateBlock : PostListQueryStateWAND {
    // the index of current block
    size_t  block_idx_;
    // current doc_id for easier manipulation
    IdType  doc_id_;

    // block size (number of entries in one block)
    const int block_size_;
    // list of records with information about individual blocks
    const vector<BlockInfo> * blocks_;
    // number of blocks - 1
    const int last_block_idx_;

    PostListQueryStateBlock(const PostList& pl, const dist_t qval, const dist_t max_term_contr, const int block_size, const vector<BlockInfo> & blocks)
        : PostListQueryStateWAND(pl, qval, max_term_contr),
          block_idx_(0),
          blocks_(& blocks),
          block_size_(block_size),
          last_block_idx_(blocks.size() - 1) {
      doc_id_ = pl.entries_[PostListQueryStateWAND::post_pos_].doc_id_;
    }

    /**
     * This method shifts the pointer the next position. Returns the current doc_id (positive)
     */
    IdType Next() {
      PostListQueryStateWAND::post_pos_ ++;
      if (PostListQueryStateWAND::post_pos_ >= PostListQueryStateWAND::post_->qty_) {
        throw new std::length_error("the end of list");
      }
      doc_id_ = PostListQueryStateWAND::post_->entries_[PostListQueryStateWAND::post_pos_].doc_id_;
      return doc_id_;
    }

    /**
     * This method shifts the pointer to a position that has the doc_id at least the given argument. It
     *  assumes that the block_idx is already set alright
     */
    bool Next(IdType min_doc_id, const bool useBlocks) {
      try {
        if (doc_id_ == min_doc_id)
          return true;

        if (useBlocks) {
          while ((*blocks_)[block_idx_].last_id < min_doc_id) {
            if (block_idx_ >= last_block_idx_) {
              throw std::length_error("the end of list");
            }
            block_idx_++;
          }
        }

        size_t block_beginning = block_size_ * block_idx_;
        if (block_beginning > PostListQueryStateWAND::post_pos_) {
          PostListQueryStateWAND::post_pos_ = block_beginning;
        }
        while (PostListQueryStateWAND::post_->entries_[PostListQueryStateWAND::post_pos_].doc_id_ < min_doc_id &&
               ++PostListQueryStateWAND::post_pos_ < PostListQueryStateWAND::post_->qty_) {
          //post_pos_ ++;
        }
        if (PostListQueryStateWAND::post_pos_ >= PostListQueryStateWAND::post_->qty_) {
          throw new std::length_error("the end of list");
        }
        doc_id_ = PostListQueryStateWAND::post_->entries_[PostListQueryStateWAND::post_pos_].doc_id_;
        LOG(LIB_INFO) << "\t\t\tNext() is shifting to position " << PostListQueryStateWAND::post_pos_ <<
        " and doc_id " << doc_id_;
        return doc_id_ == min_doc_id;
      } catch (const std::exception &e) {
        LOG(LIB_INFO) << "\t\t\tNext() generated exception: " << e;
      }
    }

    /**
     * This method shifts the block pointer to the block that might contain given ID and returns the max block contribution.
     */
    dist_t NextShallow(IdType doc_id) {
      while ((*blocks_)[block_idx_].last_id < doc_id ) {
        if (block_idx_ >= last_block_idx_) {
          throw std::length_error("the end of list");
        }
        block_idx_ ++;
      }
      return (*blocks_)[block_idx_].max_val;
    }

    dist_t GetCurrentQueryVal() const {
      return PostListQueryStateWAND::qval_ * PostListQueryStateWAND::post_->entries_[PostListQueryStateWAND::post_pos_].val_;
    }

  };

  // block size (number of entries in one block)
  int block_size_;

  // list of records with information about individual blocks
  vector<BlockInfo> blocks_;


private:
  void Next(PostListQueryStateBlock state, IdType min_doc_id_neg);



    // disable copy and assign
  DISABLE_COPY_AND_ASSIGN(BlockMaxInvIndex);
};

}   // namespace similarity

#endif     // _WAND_INV_INDEX_H_
