import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import GroupedListing from '@components/GroupedListing';
import {
    loadRounds,
    loadSubmissionsOfStatuses,
    setCurrentSubmission,
} from '@actions/submissions';
import {
    getSubmissionsByGivenStatuses,
    getCurrentSubmissionID,
    getByGivenStatusesError,
    getByGivenStatusesLoading,
    getRounds,
} from '@selectors/submissions';


const loadData = props => {
    props.loadRounds()
    props.loadSubmissions()
}

class ByRoundListing extends React.Component {
    static propTypes = {
        submissionStatuses: PropTypes.arrayOf(PropTypes.string),
        loadSubmissions: PropTypes.func,
        submissions: PropTypes.arrayOf(PropTypes.object),
        error: PropTypes.string,
        setCurrentItem: PropTypes.func,
        activeSubmission: PropTypes.number,
        shouldSelectFirst: PropTypes.bool,
        rounds: PropTypes.array,
        loading: PropTypes.bool,
    };

    componentDidMount() {
        // Update items if round ID is defined.
        if ( this.props.submissionStatuses ) {
            loadData(this.props)
        }
    }

    componentDidUpdate(prevProps) {
        const { submissionStatuses } = this.props;
        // Update entries if round ID is changed or is not null.
        if (!submissionStatuses.every(v => prevProps.submissionStatuses.includes(v))) {
            loadData(this.props)
        }
    }


    prepareOrder = () => {
        const rounds = this.props.submissions
                                 .map(v => v.round)
                                 .filter((value, index, arr) => arr.indexOf(value) === index);
        return rounds.map((v, i) => ({
            display: this.props.rounds[parseInt(v)].title,
            key: `round-${v}`,
            position: i,
            values: [v],
        }));
    }

    render() {
        const { loading, error, submissions, setCurrentItem, activeSubmission, shouldSelectFirst} = this.props;
        const isLoading = loading
        const order = this.prepareOrder();
        return <GroupedListing
                    isLoading={isLoading}
                    error={error}
                    items={submissions || []}
                    activeItem={activeSubmission}
                    onItemSelection={setCurrentItem}
                    shouldSelectFirst={shouldSelectFirst}
                    groupBy={'round'}
                    order={order}
            />;
    }
}

const mapStateToProps = (state, ownProps) => ({
    submissions: getSubmissionsByGivenStatuses(ownProps.submissionStatuses)(state),
    error: getByGivenStatusesError(ownProps.submissionStatuses)(state) ? "Something went wrong" : undefined,
    loading: getByGivenStatusesLoading(ownProps.submissionStatuses)(state),
    activeSubmission: getCurrentSubmissionID(state),
    rounds: getRounds(state),
})

const mapDispatchToProps = (dispatch, ownProps) => ({
    loadSubmissions: () => dispatch(loadSubmissionsOfStatuses(ownProps.submissionStatuses)),
    loadRounds: () => dispatch(loadRounds()),
    setCurrentItem: id => dispatch(setCurrentSubmission(id)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(ByRoundListing);
